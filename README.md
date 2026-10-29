# QSR-VisionOps---AI-Powered-Queue-Analytics-Workforce-Optimization
QSR VisionOps is an AI-powered restaurant operations platform that analyzes CCTV/video feeds and RTSP streams to monitor occupancy, queue length, wait times, and staffing needs. Features role-based dashboards, alerts with evidence snapshots, rewards, reports, analytics, and real-time operational insights.



QSR VisionOps: AI-Powered Queue Analytics and Workforce Optimization
Abstract

QSR VisionOps is an intelligent restaurant operations management platform designed to improve the efficiency of Quick Service Restaurants (QSRs) through computer vision and real-time analytics. The system utilizes video streams from CCTV cameras and uploaded video footage to monitor customer activity, estimate queue lengths, calculate occupancy levels, predict waiting times, and generate operational alerts.

By combining Artificial Intelligence, Computer Vision, and Role-Based Access Control, the platform provides restaurant managers with actionable insights that support better workforce allocation, reduced customer waiting times, and improved service quality.

Problem Statement

Managing customer flow in restaurants is a critical operational challenge. During peak hours, long queues, high occupancy levels, and inadequate staffing often result in poor customer experience and reduced operational efficiency.

Traditional monitoring approaches rely heavily on manual supervision, making it difficult to obtain accurate, timely, and scalable operational insights.

QSR VisionOps addresses this challenge by automating queue monitoring, occupancy analysis, and alert generation using AI-powered video analytics.

Objectives

The primary objectives of the project are:

Monitor customer occupancy levels automatically.
Estimate queue lengths in real time.
Predict customer waiting times.
Generate alerts for overcrowding and queue congestion.
Assist managers in workforce optimization.
Provide centralized analytics dashboards.
Enable feedback collection and service evaluation.
Support both uploaded videos and live RTSP camera streams.
System Architecture
         React Frontend
                │
                ▼
        Django REST APIs
                │
                ▼
          Analytics Engine
      (OpenCV + YOLO Model)
                │
                ▼
          PostgreSQL Database
                │
                ▼
   Dashboards, Alerts, Reports


The architecture consists of a React frontend responsible for user interaction and visualization, a Django REST backend for processing and business logic, and a Computer Vision analytics engine powered by YOLO and OpenCV for video analysis.

Technology Stack
Frontend
React.js
TypeScript
Material UI
Axios
Backend
Django
Django REST Framework
JWT Authentication
Computer Vision
YOLO (You Only Look Once)
OpenCV
Database
PostgreSQL
MongoDB (Archive Storage)
Streaming
RTSP Camera Streams
CCTV Video Sources
Modules Implemented
User Management Module

The platform supports role-based authentication and authorization.

Admin
Create and manage users
Assign roles
Manage branches
Configure cameras
Monitor alerts
Manager
Upload videos
Monitor analytics
View reports
Manage cameras
Staff
View assigned branch
Monitor performance metrics
Receive feedback
Customer
View queue information
Check estimated waiting time
Submit service feedback
Access rewards
Computer Vision Analytics Module

The analytics engine processes incoming videos and performs customer detection using YOLO.

The processing pipeline includes:

Video Input
      ↓
Frame Extraction
      ↓
Person Detection
      ↓
Customer Counting
      ↓
Analytics Generation
      ↓
Alerts Generation


Each frame is analyzed and the detected customer count is used to derive operational metrics.

Queue Analytics

Queue length is estimated from the number of people detected in each frame.

Current implementation:

queue_length = round(customer_count * 0.2)


This heuristic provides an estimate of how many customers are likely waiting in line.

The generated data is displayed through dashboard analytics and operational reports.

Waiting Time Estimation

Estimated waiting time is derived using customer count.

Current implementation:

average_wait_time = round(customer_count * 0.5)


The objective is to provide managers and customers with an approximation of expected service time.

Occupancy Analysis

Occupancy levels are estimated based on the number of detected customers.

Current implementation:

occupancy = min(customer_count * 5, 100)


Occupancy values are capped at 100% and are used to identify overcrowding situations.

Alert Management System

The system generates automated alerts whenever operational thresholds are exceeded.

Examples include:

High Occupancy Alert

Generated when restaurant occupancy crosses a predefined threshold.

Queue Congestion Alert

Generated when queue length exceeds acceptable limits.

Service Delay Alert

Generated when predicted wait times become excessive.

The alert system helps managers respond proactively to operational issues.

Evidence Snapshot Mechanism

When an alert is triggered, the system captures and stores the corresponding video frame as an evidence snapshot.

Benefits include:

Alert validation
Incident review
Historical analysis
Operational auditing

Managers can access these snapshots through the alert management dashboard.

RTSP Camera Monitoring

The platform supports real-time monitoring through RTSP-enabled surveillance cameras.

Workflow:

RTSP Camera
      ↓
OpenCV Stream Capture
      ↓
YOLO Detection
      ↓
Live Analytics
      ↓
Real-Time Alerts


This enables continuous operational monitoring without requiring manual video uploads.

Feedback Management

Customers can provide service feedback through the platform.

The system records:

Branch
Staff Member
Rating
Comments
Submission Time

This feedback enables management teams to measure employee performance and customer satisfaction.

Database Design

The core entities maintained within the system include:

User
Branch
Camera
Analytics
Alert
Feedback
Rewards

These entities collectively support the operational workflows of the restaurant ecosystem.

Key Achievements
Developed a full-stack AI-based restaurant monitoring platform.
Integrated YOLO-based customer detection.
Implemented queue analytics and occupancy monitoring.
Enabled RTSP camera support for live analytics.
Built evidence-based alert generation.
Developed role-based dashboards for multiple user categories.
Implemented customer feedback and rewards modules.
Created workforce optimization support through analytics-driven insights.
Future Enhancements
Individual customer tracking.
Advanced queue prediction using machine learning.
Heatmap-based crowd analysis.
Multi-branch comparative analytics.
Automatic staff scheduling recommendations.
Cloud deployment with scalable stream processing.
Conclusion

QSR VisionOps demonstrates how Artificial Intelligence and Computer Vision can be integrated into restaurant operations to improve efficiency, customer satisfaction, and workforce utilization. By automatically monitoring queues, occupancy levels, and operational conditions, the platform provides decision-makers with real-time insights that support smarter and faster operational decisions.
