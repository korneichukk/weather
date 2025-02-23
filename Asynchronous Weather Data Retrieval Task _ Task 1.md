You need to create a system for asynchronous weather data processing that:

1. Accepts a list of cities from the user via an HTTP POST request.  
2. Fetches weather data for each city using an external API.  
3. Saves the processed results in a specific format for further analysis.

However, you must account for the following complexities:

### **Constraints:**

1. **Unreliable API:** The available weather API frequently returns errors or delays and provides raw data with ambiguous labels.  
2. **Cities in Multiple Languages:** Input may include city names in different languages and with typos (e.g., "Киев", "Kyiv", "Paris").  
3. **Complex Data Validation:** Some data from the API may be incomplete or incorrect (e.g., temperature missing units).  
4. **Task Distribution:** Results must be split into files based on geographic regions (e.g., Europe, Asia).

### **Functionality:**

**POST /weather:**  
Accepts a JSON request:  
`{`  
  `"cities": ["Киев", "New York", "Токио", "Londn"]`  
`}`

1.   
   * Cleans and normalizes the input (corrects city names).  
   * Initializes an asynchronous task to process the data.  
   * Returns a task ID.  
2. **GET /tasks/\<task\_id\>:**  
   * Returns the task status: `running`, `completed`, `failed`.  
   * If completed, provides a link to the file with results.  
3. **GET /results/\<region\>:**  
   * Returns a list of cities and their data for the specified region.

### **Data Processing:**

1. For each city:  
   * Fetch weather data from the API.  
   * Filter out cities with invalid data (e.g., temperature outside the range of \-50 to \+50 °C).  
   * Classify data by region.  
2. Save results in the folder `weather_data/<region>/task_<task_id>.json`.

### **Example Workflow:**

#### **Input:**

`{`  
  `"cities": ["Киев", "Londn", "New York", "Токио"]`  
`}`

#### **Intermediate Processing:**

1. "Киев" → "Kyiv" (normalization).  
2. "Londn" → "London" (typo correction).  
3. The API returns errors for "Токио".

#### **Output:**

`{`  
  `"status": "completed",`  
  `"results": {`  
    `"Europe": [`  
      `{ "city": "Kyiv", "temperature": -2.0, "description": "snow" },`  
      `{ "city": "London", "temperature": 10.0, "description": "rain" }`  
    `],`  
    `"America": [`  
      `{ "city": "New York", "temperature": 15.0, "description": "clear sky" }`  
    `]`  
  `}`  
`}`

### **Requirements:**

* Use Celery and Redis for asynchronous processing.  
* API errors must be logged with error details.  
* Code must be structured to scale for multiple regions.  
* Additional implementation requirements:  
  * Validate input using regular expressions.  
  * Support API keys for multiple external services.

