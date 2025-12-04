FROM public.ecr.aws/lambda/python:3.11

# Copy requirements file
COPY requirements.txt ${LAMBDA_TASK_ROOT}/

# Install dependencies
RUN pip install --no-cache-dir -r ${LAMBDA_TASK_ROOT}/requirements.txt

# Copy application code
COPY app/ ${LAMBDA_TASK_ROOT}/app/

# Copy handler
COPY lambda_handler.py ${LAMBDA_TASK_ROOT}/

# Set the CMD to your handler
CMD ["lambda_handler.handler"]
