from unicodedata import name
from urllib import response
from django.shortcuts import render
from django.http import JsonResponse,StreamingHttpResponse
from django.conf import settings
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail, EmailMessage
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import openai, os, json, stripe
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .serializer import MyTokenObtainPairSerializer

def index(request):
    return render(request, 'index.html')


# myapp/views.py


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer  # Create this serializer (see next step)

class MyTokenRefreshView(TokenRefreshView):
    pass



@csrf_exempt
def chat_view(request):
    if request.method == 'POST':
        data = json.loads(request.POST.get('values'))

        duration = data["data"].get('rangeInput', 7)
        language = data["data"].get('language')
        destination = data["data"].get('destination')
        budget = data["data"].get('color_mode')
        purpose = data["data"].get('color_mode_purpose')
        budget = 1000 if budget == "Budget" else (2000 if budget == "Medium" else 3000)
        hotelValue = data["data"].get('hotelValue')
        hotelValue = 3 if hotelValue is None else hotelValue
        # Set up the OpenAI API client with your API key
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
        return StreamingHttpResponse(generate_response(), headers={'X-Accel-Buffering': 'no'})


    else:
        return render(request, 'error.html', {})


@csrf_exempt
def stripe_config(request):
    if request.method == 'GET':
        stripe_config = {'publicKey': settings.STRIPE_PUBLISHABLE_KEY}
        return JsonResponse(stripe_config, safe=False)


@csrf_exempt
def create_checkout_session(request):
    if request.method == 'GET':
        domain_url = 'https://0419-2405-201-5004-706a-5979-7ffb-9290-b780.ngrok-free.app/'
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            checkout_session = stripe.checkout.Session.create(
                success_url=domain_url + 'success/',
                cancel_url=domain_url + 'cancelled/',
                payment_method_types=['card'],
                mode='payment',
                line_items=[{
                    'price_data':
                    {
                        'currency': 'inr',
                        'unit_amount': 10000,
                        'product_data': {'name': 'Travelling', },
                    },
                    'quantity': 1,
                },
                ]
            )
            return JsonResponse({'sessionId': checkout_session['id']})
        except Exception as e:
            return JsonResponse({'error': str(e)})

# Success view
def success(request):
    return render(request, 'success.html')

# Cancel view
def cancelled(request):
    return render(request, 'cancelled.html')


@csrf_exempt
def send_emails_user(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        name = request.POST.get('name')
        chatbot_itinerary = request.POST.get('response')
        try:
            chatbot_itinerary = chatbot_itinerary.replace('Connect to travel agent  to get concise information about your destination', '')

        except:
            chatbot_itinerary = request.POST.get('response')
        if email:
            # Render the HTML template with the email content
            html_message = render_to_string('email_template.html', {'name': name, 'response': chatbot_itinerary})


            # Create a plain text version of the email
            plain_message = strip_tags(html_message)



            # Create an EmailMultiAlternatives object
            subject = 'Thank you for contacting expert4travel agent'
            from_email = settings.EMAIL_HOST_USER
            to_email = [email]

            email_message = EmailMultiAlternatives(subject, plain_message, from_email, to_email)
            email_message.attach_alternative(html_message, "text/html")

            # Send the email
            email_message.send()

            return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Email parameter is missing.'})


@csrf_exempt
def send_email_agent(request):
    if request.method == 'POST':
        destination = request.POST.get('destination')
        budget = request.POST.get('budget')
        duration = request.POST.get('duration')
        chatbot_itinerary = request.POST.get('response')
        email = request.POST.get('email')
        name = request.POST.get('name')
        contactNumber = request.POST.get('contact')
        try:
            chatbot_itinerary = chatbot_itinerary.replace('Connect to travel agent  to get concise information about your destination', '')

        except:
            chatbot_itinerary = request.POST.get('response')
        if email:
            subject = 'User query and chatbot response for itinerary'
            context = {
                'name': name,
                'contactNumber': contactNumber,
                'destination': destination,
                'budget': budget,
                'duration': duration,
                'email': email,
                'response': chatbot_itinerary,
            }
            message = render_to_string('email_template_agent.html', context)

            email_from = settings.EMAIL_HOST_USER
            recipient_list = ['nitish@snakescript.com']
            cc_list = ['kapil@snakescript.com', "vanya@expert4travel.com"]

            email = EmailMessage(subject, message, email_from, recipient_list, bcc=cc_list)
            email.content_subtype = 'html'  # Set the content type as HTML
            email.send()

            return JsonResponse({'success': True})
    # Return an error response if email parameter is missing
    return JsonResponse({'success': False, 'error': 'Email parameter is missing.'})
