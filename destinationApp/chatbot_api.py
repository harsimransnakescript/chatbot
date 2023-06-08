from rest_framework.views import APIView
from rest_framework.response import Response 
import openai, os
from rest_framework.parsers import JSONParser
from django.http import StreamingHttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from django.http import HttpResponseBase





@permission_classes([IsAuthenticated])
class ChatBotView(APIView):
    
    def post(self, request):
        
        data = JSONParser().parse(request)
        print('**************', data)
        duration = data["data"].get('rangeInput', 7)
        language = data["data"].get('language')
        destination = data["data"].get('destination')
        budget = data["data"].get('color_mode')
        budget = 1000 if budget == "Budget" else (2000 if budget == "Medium" else 3000)
        hotelValue = data["data"].get('hotelValue')
        hotelValue = 3 if hotelValue is None else hotelValue
        openai.api_key = os.environ.get('OPENAI_API_KEY')


        # Define the prompt for the GPT-3 API
        prompt = [
            {
                "role": "user",
                "content": f"INSTRUCTIONS,\n1. Act as a travel expert and provide information to the users regarding different places.\n2. IMPORTANT! Please don't say As an AI language model, I can't help you.\n3. IMPORTANT! Please add markdown URLs to the itinerary and accommodation every time with the format '?q' should always come after the 'Search' [Visit Red Fort](https://www.tripadvisor.in/Search?q=Red_Fort_Lal_Quila)\n4. Markdown strictly follow this URL format '?q' should always come after the 'Search' [Visit Red Fort](https://www.tripadvisor.in/Search?q=Red_Fort_Lal_Quila)\n5. Markdown URL should come in the case of both the itinerary and hotels"
            },
            {
                "role": "user",
                "content": f"I'm planning a {duration}-day trip to {destination} and I'm looking for advice on how to make the most of my time there. My budget is in the range of up to {budget} USD, and I want to experience the best that {destination} has to offer. Can you help me create an itinerary that maximizes my budget and allows me to see all the must-see attractions and experiences?\n\nAdditionally, I'm interested in tips on efficient transportation around the city and how to save money in that aspect. Could you provide recommendations on the best way to get around the city and save money on transportation?\n\nLastly, I'd like to make sure I experience the best of {destination} on my budget ranging up to {budget} USD. Do you have any suggestions or insider tips on how to make the most out of my trip and get the best value for my money?\n\nAdditionally, I would like to know your recommendations for {hotelValue} star hotels or accommodations for each place and of each day in {destination}. Please suggest options that fit within my budget of up to {budget} USD and provide details such as the name of the hotel, its location, and any special features or amenities it offers in list format.\n\nPlease provide an hourly breakdown for each day, starting from morning until evening of a {duration}-day trip to {destination} in {language} language. Include the activities, attractions, and experiences you would like to do, along with their respective time slots. Please make sure to specify the start and end times at the beginning of each line, and avoid writing Morning, Afternoon, and Evening at the beginning. Please use markdown URLs for each activity in the following format:\n\n**Itinerary Example:**\n\n- 09:00 - 10:30: Visit [Red Fort](https://www.tripadvisor.in/Search?q=Red_Fort_Lal_Quila)\n- 11:00 - 12:30: Explore [Historic District](https://www.tripadvisor.in/Search?q=Historic_District)\n- 13:00 - 14:30: Lunch at [Local Restaurant](https://www.tripadvisor.in/Search?q=Local_Restaurant)\n- 15:00 - 16:30: Take a [Boat Tour](https://www.tripadvisor.in/Search?q=Boat_Tour)\n- 17:00 - 18:30: Enjoy [City Park](https://www.tripadvisor.in/Search?q=City_Park)"
            },
            {
                "role": "user",
                "content": "Response:"
            }
        ]

        # Call the GPT-3 API to generate a response
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=prompt,
            temperature=0.0,
            stream=True,
            top_p=1.0,
        )
        
        test = []
        def generate_response():
            for chunk in response:
                chunk_message = chunk['choices'][0]['delta']
                test.append(chunk_message.get("content", ''))
                yield chunk_message.get("content", '')

        # use Django's StreamingHttpResponse to send the response messages as a stream to the frontend
        return StreamingHttpResponse(generate_response(),headers={'X-Accel-Buffering': 'no'}, content_type='application/octet-stream')
    

class ApiUserRegister(APIView):

    def post(self, request):

        response = {} 
        try:
            data = JSONParser().parse(request)
            if data.get('username') is None:
                response['message'] = 'key username not found'
                raise Exception('key username not found')

            if data.get('password') is None:
                response['message'] = 'key password not found'
                raise Exception('key password not found')
            check_user = User.objects.filter(
                username=data.get('username')).first()
            if check_user:
                response['message'] = 'username already taken'
                raise Exception('username already taken')

            user_obj = User.objects.create(email=data.get('username'),
                                           username=data.get('username'))
            user_obj.set_password(data.get('password'))
            user_obj.save()

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user_obj)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            
            response['message'] = 'User Created Successfully'
            response['status'] = 200
            response['access_token'] = access_token
            response['refresh_token'] = refresh_token
        except Exception as e:
            print(e)

        return Response(response)
