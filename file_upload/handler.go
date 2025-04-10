package main

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

type Handler struct {
	rabbitMQ *RabbitMQ
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
