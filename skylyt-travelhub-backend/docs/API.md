# Skylyt TravelHub API Documentation

## Overview
The Skylyt TravelHub API provides comprehensive travel booking services including hotel reservations, car rentals, and bundle packages.

## Base URL
- Development: `http://localhost:8000`
- Production: `https://api.skylyt.com`

## Authentication
All protected endpoints require a Bearer token in the Authorization header:
```
Authorization: Bearer <your_access_token>
```

## Endpoints

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Token refresh
- `POST /api/v1/auth/forgot-password` - Password reset request
- `POST /api/v1/auth/reset-password` - Password reset

### Users
- `GET /api/v1/users/me` - Get current user profile
- `PUT /api/v1/users/me` - Update user profile
- `GET /api/v1/users/me/bookings` - Get user bookings
- `GET /api/v1/users/me/favorites` - Get user favorites

### Hotels
- `GET /api/v1/hotels/search` - Search hotels
- `GET /api/v1/hotels/{hotel_id}` - Get hotel details
- `POST /api/v1/hotels/{hotel_id}/check-availability` - Check availability

### Cars
- `GET /api/v1/cars/search` - Search cars
- `GET /api/v1/cars/{car_id}` - Get car details
- `POST /api/v1/cars/{car_id}/check-availability` - Check availability

### Bookings
- `POST /api/v1/bookings` - Create booking
- `GET /api/v1/bookings` - List user bookings
- `GET /api/v1/bookings/{booking_id}` - Get booking details
- `DELETE /api/v1/bookings/{booking_id}` - Cancel booking

### Payments
- `POST /api/v1/payments/process` - Process payment
- `GET /api/v1/payments/{payment_id}` - Get payment status
- `POST /api/v1/payments/{payment_id}/refund` - Process refund

## Error Handling
The API uses standard HTTP status codes and returns errors in JSON format:
```json
{
  "detail": "Error message",
  "error_code": "SPECIFIC_ERROR_CODE"
}
```

## Rate Limiting
- Authentication endpoints: 10 requests per 5 minutes
- Search endpoints: 50 requests per 5 minutes
- Booking endpoints: 20 requests per 5 minutes

## Interactive Documentation
Visit `/docs` for Swagger UI or `/redoc` for ReDoc (development only).