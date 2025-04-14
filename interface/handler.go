package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/gin-gonic/gin"
)

type Handler struct {
	rabbitMQ *RabbitMQ
}

type RequestBody struct {
	Brand        string  `json:"brand"`
	Year         int     `json:"year"`
	Engine_Size  float64 `json:"engine_size"`
	Fuel_Type    string  `json:"fuel_type"`
	Transmission string  `json:"transmission"`
	Mileage      int     `json:"mileage"`
	Condition    string  `json:"condition"`
	Model        string  `json:"model"`
}

func NewHandler(rabbitMQ *RabbitMQ) *Handler {
	return &Handler{rabbitMQ: rabbitMQ}
}

// UploadFile godoc
// @Summary Uploads a file
// @Description Accepts a file and sends its name to RabbitMQ
// @Tags files
// @Accept multipart/form-data
// @Produce json
// @Param file formData file true "File to upload"
// @Success 200 {string} string "ok"
// @Failure 400 {string} string "bad request"
// @Router /upload [post]
func (h *Handler) UploadFile(c *gin.Context, queueName string, filePath string) {
	file, err := c.FormFile("file")
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "No file provided"})
		return
	}

	// Save file
	if err := c.SaveUploadedFile(file, filePath+"/"+file.Filename); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save file"})
		return
	}

	// Send message to RabbitMQ
	err = h.rabbitMQ.Publish(queueName, []byte(file.Filename))
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to send message to RabbitMQ"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "File uploaded and message sent"})
}

func (h *Handler) HealthCheck(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{"message": "ok"})
}

// @Summary Predict something
// @Description Processes a prediction request
// @Tags predict
// @Accept json
// @Produce json
// @Param input body map[string]interface{} true "Prediction input"
// @Success 200 {object} map[string]interface{}
// @Failure 400 {object} map[string]string
// @Router /predict [post]
func (h *Handler) Predict(c *gin.Context) {
	var requestBody RequestBody
	if err := c.ShouldBindJSON(&requestBody); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request body"})
		return
	}

	jsonBody, err := json.Marshal(requestBody)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to marshal request body"})
		return
	}

	fmt.Println("Sending request to Python worker with body:", string(jsonBody))

	resp, err := http.Post("http://ml-inference:5001/predict/onnx", "application/json", bytes.NewReader(jsonBody))
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to send request to Python worker"})
		return
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to get prediction"})
		return
	}

	var responseBody map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&responseBody); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to decode response"})
		return
	}
	c.JSON(http.StatusOK, responseBody)
}
