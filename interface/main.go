package main

import (
	"os"

	swaggerFiles "github.com/swaggo/files"
	ginSwagger "github.com/swaggo/gin-swagger"

	"github.com/gin-gonic/gin"

	_ "interface/docs" // Import the generated docs package
)

// @title File Upload API
// @version 1.0
// @description A simple file upload API with RabbitMQ and Python worker
// @host localhost:8080
// @BasePath /
func main() {
	// Get from env variable
	connString := os.Getenv("RABBITMQ_URL")
	queueName := os.Getenv("RABBITMQ_QUEUE")
	filePath := os.Getenv("FILE_PATH")

	// Initialize RabbitMQ connection
	rabbitMQ, err := NewRabbitMQ(connString, queueName)
	if err != nil {
		panic(err)
	}
	defer rabbitMQ.Close()

	handler := NewHandler(rabbitMQ)

	r := gin.Default()
	r.POST("/upload", func(c *gin.Context) {
		handler.UploadFile(c, queueName, filePath)
	})
	r.GET("/health", handler.HealthCheck)
	r.GET("/swagger/*any", ginSwagger.WrapHandler(swaggerFiles.Handler))

	r.Run(":8080")
}
