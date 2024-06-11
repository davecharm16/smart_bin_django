import json
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from openai import OpenAI


# Create your views here.
@csrf_exempt
@require_POST
def analyze_data(request):
    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
    )
    try:
        data = json.loads(request.body)
        input_waste_data = data.get('waste_data')
        input_fill_data = data.get('fill_level_data')
        api_secret = data.get('api_key')
        if (api_secret == os.environ.get("API_SECRET")):
            return JsonResponse({'error': 'Wrong API KEY'}, status=400)
        if not input_waste_data or not input_fill_data:
            return JsonResponse({'error': 'Missing data'}, status=400)
        prompt_message = f"""
        You are a waste management data analyst. Analyze the following waste
        data to generate a report on waste disposal patterns and bin fill
        levels.
        Waste Data (Disposal Events):
        {input_waste_data}
        Waste Data (Fill Levels):
        {input_fill_data}
        If the provided data does not meet the format requirements or if there
        is not enough data for meaningful analysis (e.g., less than 10 data
        points of each type), please provide a user message explaining the
        issue and suggesting how to resolve it.
        Otherwise, generate the report as follows:
        Report:
        Waste Disposal Patterns:
        * Overall waste disposal trends over time (e.g., increasing,
        decreasing, peak hours/days)
        * Breakdown of waste disposal by type (e.g., plastic, organic, paper)
        * Distribution of waste across different bins
        * Identification of most frequently used bins
        * Any significant outliers or unusual patterns in disposal behavior
        Bin Fill Levels:
        * Analysis of bin fill levels over time (e.g., average fill rates,
        peak fill times)
        * Identification of bins that tend to fill up quickly or slowly
        * Correlation between waste disposal events and bin fill levels
        Recommendations:
        * Suggestions for optimizing bin placement
        or collection schedules
        based on both disposal patterns and fill levels
        """
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                    "content": "You are a waste management data analyst."},
                {"role": "user", "content": prompt_message}
            ]
        )
        message_content = response.choices[0].message.content
        if message_content.startswith("Report:"):
            return JsonResponse({'report': message_content[7:].strip()})
        else:
            return JsonResponse({'message': message_content})
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
