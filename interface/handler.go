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
	ModelGroup  string `json:"model_group" default:"A"`
	Model       int    `json:"model" default:"180"`
	Kilometers  int    `json:"kilometers" default:"5000"`
	FuelType    string `json:"fuel_type" default:"Diesel"`
	GearType    string `json:"gear_type" default:"Manual"`
	VehicleType string `json:"vehicle_type" default:"Sedan Car"`
	AgeInMonths int    `json:"age_in_months" default:"12"`
	Color       string `json:"color" default:"Black"`
	Line        string `json:"line" default:"Sportline"`
	Doors       string `json:"doors" default:"4 to 5"`
	Seats       string `json:"seats" default:"1 to 3"`
	Climate     string `json:"climate" default:"Air Conditioning"`
}

func NewHandler(rabbitMQ *RabbitMQ) *Handler {
	return &Handler{rabbitMQ: rabbitMQ}
}

func (h *Handler) UploadFile(c *gin.Context, queueName string, filePath string) {
	// Get file from request
	file, err := c.FormFile("file")
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "No file provided"})
		return
	}

	// Save file to the specified path
	fullFilePath := filePath + "/" + file.Filename
	if err := c.SaveUploadedFile(file, fullFilePath); err != nil {
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

func (h *Handler) Predict(c *gin.Context, mlUrl string) {
	// Get request body
	var requestBody RequestBody
	if err := c.ShouldBindJSON(&requestBody); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request body"})
		return
	}

	// Marshal request body to JSON
	jsonBody, err := json.Marshal(requestBody)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to marshal request body"})
		return
	}

	fmt.Println("Sending request to Python worker with body:", string(jsonBody))

	// Send request to Python worker
	resp, err := http.Post(mlUrl, "application/json", bytes.NewReader(jsonBody))
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to send request to Python worker"})
		return
	}
	defer resp.Body.Close()

	// Check response status
	if resp.StatusCode != http.StatusOK {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to get prediction"})
		return
	}

	// Decode response body
	var responseBody map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&responseBody); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to decode response"})
		return
	}
	c.JSON(http.StatusOK, responseBody)
}

func (h *Handler) HealthCheck(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{"message": "ok"})
}
