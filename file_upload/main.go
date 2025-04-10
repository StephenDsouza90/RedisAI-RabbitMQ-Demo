package main

import (
	swaggerFiles "github.com/swaggo/files"
	ginSwagger "github.com/swaggo/gin-swagger"

	"github.com/gin-gonic/gin"
)

// @title File Upload API
// @version 1.0
// @description A simple file upload API with RabbitMQ and Python worker
// @host localhost:8080
// @BasePath /
func main() {
	// Initialize RabbitMQ connection
	rabbitMQ, err := NewRabbitMQ("amqp://guest:guest@rabbitmq:5672/")
	if err != nil {
		panic(err)
	}
	defer rabbitMQ.Close()

	handler := NewHandler(rabbitMQ)

	r := gin.Default()
	r.POST("/upload", handler.UploadFile)
	r.GET("/health", handler.HealthCheck)
	r.GET("/swagger/*any", ginSwagger.WrapHandler(swaggerFiles.Handler))

	r.Run(":8080")
}
