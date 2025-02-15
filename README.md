# TTC API Documentation

This project provides an API for interacting with the Toronto Transit Commission (TTC) data. The API allows users to register, add routes, remove routes, get a list of routes, get route information, and get predictions for a specific stop and route.



## Endpoints

`url:`

### `/signup`

- **Method:** POST
- **Description:** Register a new user.
- **Arguments:**
  - None
- **Headers:**
  - `email`: string
  - `password`: string

### `/add_route`

- **Method:** POST
- **Description:** Add a route to the user's data.
- **Arguments:**
  - `route`: string
- **Headers:**
  - `token`: string (Bearer token for authentication)

### `/remove_route`

- **Method:** GET
- **Description:** Remove a route from the user's data.
- **Arguments:**
  - None
- **Headers:**
  - `token`: string (Bearer token for authentication)

### `/routes`

- **Method:** GET
- **Description:** Get a list of routes.
- **Arguments:**
  - None
- **Headers:**
  - `token`: string (Bearer token for authentication)

### `/route_info`

- **Method:** GET
- **Description:** Get information about a specific route.
- **Arguments:**
  - `r`: string (Route tag, optional)
- **Headers:**
  - `token`: string (Bearer token for authentication)

### `/predictions`

- **Method:** GET
- **Description:** Get predictions for a specific stop and route.
- **Arguments:**
  - `s`: string (Stop ID, required)
  - `rt`: string (Route tag, optional)
- **Headers:**
  - `token`: string (Bearer token for authentication)


