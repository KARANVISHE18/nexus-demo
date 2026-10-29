FROM python:3.12-slim
WORKDIR /app
# Copy requirements first so this layer is cached when only code changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Install pytest for the test runner
RUN pip install --no-cache-dir pytest
COPY . .
# Fix the add function to perform addition instead of subtraction
RUN sed -i 's/return a - b/return a + b/' app.py
EXPOSE 5000
CMD ["python", "app.py"]
