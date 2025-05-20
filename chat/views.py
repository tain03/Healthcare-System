import json
import time
import random
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.conf import settings

from .models import Conversation, Message, AIResponse
from core.models import User, Patient, Doctor
from .services import llm_service

# Set up logging
logger = logging.getLogger(__name__)

@login_required
def chat_home(request):
    """Display the chat home page with a list of conversations"""
    user = request.user

    # Get search query
    search_query = request.GET.get('q', '')

    # Get all conversations where the user is either the initiator or receiver
    conversations_query = Conversation.objects.filter(
        Q(initiator=user) | Q(receiver=user),
        is_active=True
    )

    # Apply search filter if provided
    if search_query:
        # Search in conversation titles
        conversations_with_matching_title = conversations_query.filter(title__icontains=search_query)

        # Search in messages content
        conversations_with_matching_messages = conversations_query.filter(
            messages__content__icontains=search_query
        ).distinct()

        # Combine results
        conversations = (conversations_with_matching_title | conversations_with_matching_messages).distinct().order_by('-updated_at')
    else:
        conversations = conversations_query.order_by('-updated_at')

    # Get AI assistant conversation or create one if it doesn't exist
    ai_conversation, created = Conversation.objects.get_or_create(
        initiator=user,
        conversation_type='ai_assistant',
        defaults={
            'title': 'AI Health Assistant',
            'is_active': True
        }
    )

    context = {
        'conversations': conversations,
        'ai_conversation': ai_conversation,
        'search_query': search_query
    }

    return render(request, 'chat/home.html', context)

@login_required
def conversation_detail(request, conversation_id):
    """Display a specific conversation and its messages"""
    user = request.user
    conversation = get_object_or_404(
        Conversation.objects.filter(Q(initiator=user) | Q(receiver=user)),
        id=conversation_id
    )

    # Get search query
    search_query = request.GET.get('q', '')

    # Mark all unread messages as read
    unread_messages = Message.objects.filter(
        conversation=conversation,
        is_read=False
    ).exclude(sender=user)

    for message in unread_messages:
        message.is_read = True
        message.save()

    # Get all messages for this conversation
    messages_query = Message.objects.filter(conversation=conversation)

    # Apply search filter if provided
    if search_query:
        messages_list = messages_query.filter(content__icontains=search_query).order_by('timestamp')
        # Highlight the search term in the messages
        for message in messages_list:
            message.content = message.content.replace(
                search_query,
                f'<span class="bg-warning">{search_query}</span>'
            )
    else:
        messages_list = messages_query.order_by('timestamp')

    # If this is an AI conversation, we need to handle it differently
    is_ai_conversation = conversation.conversation_type == 'ai_assistant'

    # Get available doctors for patient to start a conversation with
    available_doctors = []
    if user.user_type == 'patient':
        available_doctors = Doctor.objects.all()

    # Get all conversations for the sidebar
    conversations = Conversation.objects.filter(
        Q(initiator=user) | Q(receiver=user),
        is_active=True
    ).order_by('-updated_at')

    # Get AI assistant conversation
    ai_conversation = Conversation.objects.filter(
        initiator=user,
        conversation_type='ai_assistant'
    ).first()

    context = {
        'conversation': conversation,
        'conversations': conversations,
        'ai_conversation': ai_conversation,
        'chat_messages': messages_list,
        'is_ai_conversation': is_ai_conversation,
        'available_doctors': available_doctors,
        'search_query': search_query
    }

    return render(request, 'chat/conversation.html', context)

@login_required
def create_conversation(request):
    """Create a new conversation"""
    if request.method == 'POST':
        receiver_id = request.POST.get('receiver')
        title = request.POST.get('title')

        if not receiver_id or not title:
            messages.error(request, 'Please provide all required information')
            return redirect('chat:home')

        try:
            receiver = User.objects.get(id=receiver_id)

            # Determine conversation type based on user roles
            if request.user.user_type == 'patient' and receiver.user_type == 'doctor':
                conversation_type = 'patient_doctor'
            elif request.user.user_type == 'patient':
                conversation_type = 'patient_support'
            elif request.user.user_type == 'doctor':
                conversation_type = 'doctor_support'
            else:
                conversation_type = 'patient_support'  # Default

            # Check if conversation already exists
            existing_conversation = Conversation.objects.filter(
                Q(initiator=request.user, receiver=receiver) |
                Q(initiator=receiver, receiver=request.user),
                is_active=True
            ).first()

            if existing_conversation:
                return redirect('chat:conversation', conversation_id=existing_conversation.id)

            # Create new conversation
            conversation = Conversation.objects.create(
                title=title,
                initiator=request.user,
                receiver=receiver,
                conversation_type=conversation_type
            )

            return redirect('chat:conversation', conversation_id=conversation.id)

        except User.DoesNotExist:
            messages.error(request, 'Selected user does not exist')
            return redirect('chat:home')

    return redirect('chat:home')

@login_required
@csrf_exempt
def send_message(request, conversation_id):
    """Send a message in a conversation"""
    if request.method == 'POST':
        user = request.user
        conversation = get_object_or_404(
            Conversation.objects.filter(Q(initiator=user) | Q(receiver=user)),
            id=conversation_id
        )

        content = request.POST.get('content')
        message_type = request.POST.get('message_type', 'text')

        # Handle file uploads
        attachment = None
        if request.FILES and 'attachment' in request.FILES:
            attachment = request.FILES['attachment']
            file_name = attachment.name.lower()

            # Determine message type based on file extension
            if file_name.endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
                message_type = 'image'
            else:
                message_type = 'file'

        if not content and not attachment:
            return JsonResponse({'status': 'error', 'message': 'Message content or attachment is required'})

        # Create the message
        message = Message.objects.create(
            conversation=conversation,
            sender=user,
            content=content or '',  # Empty string if no content
            message_type=message_type,
            attachment=attachment
        )

        # Update conversation timestamp
        conversation.updated_at = timezone.now()
        conversation.save()

        # Prepare response data
        message_data = {
            'id': message.id,
            'content': message.content,
            'message_type': message.message_type,
            'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'sender_name': user.get_full_name(),
            'is_self': True
        }

        # Add attachment URL if present
        if message.attachment:
            message_data['attachment_url'] = message.attachment.url

        # If this is an AI conversation, generate an AI response
        if conversation.conversation_type == 'ai_assistant':
            # Call AI service to get response
            start_time = time.time()
            ai_response = generate_ai_response(content)
            response_time = time.time() - start_time

            # Format the AI response with HTML line breaks
            formatted_response = ai_response.replace('\n\n', '<br><br>').replace('\n', '<br>')

            # Create AI message
            ai_message = Message.objects.create(
                conversation=conversation,
                sender=None,  # AI has no sender
                content=formatted_response,
                message_type='ai_response',
                is_read=True  # Mark as read immediately
            )

            # Add metadata to the message content to indicate if it's from LLM or rule-based
            # This will be parsed by the frontend
            is_llm_response = not (random.random() < getattr(settings, 'LLM_RULE_THRESHOLD', 0.7))
            response_type = "llm" if is_llm_response else "rule"

            # Create AI response record
            AIResponse.objects.create(
                message=ai_message,
                prompt=content,
                response_time=response_time
            )

            # Update conversation timestamp again
            conversation.updated_at = timezone.now()
            conversation.save()

            return JsonResponse({
                'status': 'success',
                'message': 'Message sent successfully',
                'message_data': message_data,
                'ai_response': {
                    'id': ai_message.id,
                    'content': formatted_response,
                    'timestamp': ai_message.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'response_type': response_type
                }
            })

        return JsonResponse({
            'status': 'success',
            'message': 'Message sent successfully',
            'message_data': message_data
        })

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
def get_messages(request, conversation_id):
    """Get all messages for a conversation (for AJAX polling)"""
    user = request.user
    conversation = get_object_or_404(
        Conversation.objects.filter(Q(initiator=user) | Q(receiver=user)),
        id=conversation_id
    )

    # Get timestamp from request to only return newer messages
    last_timestamp = request.GET.get('last_timestamp')

    if last_timestamp:
        messages_list = Message.objects.filter(
            conversation=conversation,
            timestamp__gt=last_timestamp
        ).order_by('timestamp')
    else:
        messages_list = Message.objects.filter(conversation=conversation).order_by('timestamp')

    # Mark messages as read
    unread_messages = messages_list.filter(is_read=False).exclude(sender=user)
    for message in unread_messages:
        message.is_read = True
        message.save()

    # Format messages for JSON response
    messages_data = []
    for message in messages_list:
        sender_name = message.sender.get_full_name() if message.sender else "AI Assistant"
        message_data = {
            'id': message.id,
            'content': message.content,
            'sender_id': message.sender.id if message.sender else None,
            'sender_name': sender_name,
            'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'message_type': message.message_type,
            'is_self': message.sender == user if message.sender else False
        }

        # Add attachment URL if present
        if message.attachment:
            message_data['attachment_url'] = message.attachment.url
            message_data['attachment_name'] = message.attachment.name.split('/')[-1]  # Get just the filename

        messages_data.append(message_data)

    return JsonResponse({'chat_messages': messages_data})

@login_required
def rate_ai_response(request, message_id):
    """Rate an AI response"""
    if request.method == 'POST':
        rating = request.POST.get('rating')

        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                return JsonResponse({'status': 'error', 'message': 'Rating must be between 1 and 5'})

            message = get_object_or_404(Message, id=message_id, message_type='ai_response')

            # Get or create AI response record
            ai_response, created = AIResponse.objects.get_or_create(
                message=message,
                defaults={
                    'prompt': '',
                    'response_time': 0.0
                }
            )

            ai_response.feedback = rating
            ai_response.save()

            return JsonResponse({'status': 'success', 'message': 'Rating submitted successfully'})

        except (ValueError, TypeError):
            return JsonResponse({'status': 'error', 'message': 'Invalid rating value'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
def get_unread_count(request):
    """Get the total count of unread messages for the user"""
    user = request.user

    # Get all conversations where the user is either the initiator or receiver
    conversations = Conversation.objects.filter(
        Q(initiator=user) | Q(receiver=user),
        is_active=True
    )

    # Count unread messages
    total_unread = 0
    unread_by_conversation = {}

    for conversation in conversations:
        unread_count = conversation.get_unread_count(user)
        if unread_count > 0:
            total_unread += unread_count
            unread_by_conversation[str(conversation.id)] = {
                'count': unread_count,
                'title': conversation.title
            }

    return JsonResponse({
        'total_unread': total_unread,
        'unread_by_conversation': unread_by_conversation
    })

# Helper function to generate AI responses
def generate_ai_response(prompt):
    """Generate an AI response based on the prompt"""
    # Log the incoming prompt
    logger.info(f"Generating AI response for prompt: {prompt[:50]}...")

    # Get the rule threshold from settings
    rule_threshold = getattr(settings, 'LLM_RULE_THRESHOLD', 0.7)

    # Add system prompt to guide the AI's response
    system_prompt = """You are an AI health assistant in a healthcare system. Your role is to:
1. Provide accurate, helpful, and concise responses to health-related questions
2. Always prioritize patient safety and well-being
3. Be empathetic and professional in your communication
4. Use simple, clear language that patients can understand
5. Focus on providing general health information and guidance
6. Never make definitive diagnoses or prescribe treatments
7. Keep responses brief and to the point
8. Avoid redundant advice about consulting healthcare professionals (this will be added automatically)
9. Format your response with single line breaks between sentences
10. Keep each point concise and easy to read
11. Always response in one or two sentences and less than 50 words.

Please respond to the following question while keeping these guidelines in mind:"""

    # Combine system prompt with user's question
    enhanced_prompt = f"{system_prompt}\n\n{prompt}"

    # Simple rule-based responses for common patterns
    prompt_lower = prompt.lower()

    # Determine if we should use rule-based response or LLM
    use_rules = random.random() < rule_threshold

    # For certain patterns, always use rule-based responses for reliability
    force_rules = False

    # Greeting patterns - always use rules for these simple exchanges
    if any(greeting in prompt_lower for greeting in ['hello', 'hi', 'hey', 'greetings']):
        force_rules = True
        rule_response = random.choice([
            "Hello! I'm your AI health assistant. How can I help you today?",
            "Hi there! How are you feeling today?",
            "Greetings! I'm here to assist with any health-related questions."
        ])

    # Thank you patterns - always use rules for these simple exchanges
    elif any(thanks in prompt_lower for thanks in ['thank you', 'thanks', 'thx', 'thank']):
        force_rules = True
        rule_response = random.choice([
            "You're welcome! Is there anything else I can help you with?",
            "Happy to help! Let me know if you have any other questions.",
            "My pleasure! I'm here anytime you need health information."
        ])

    # Emergency situations - always use rules for critical information
    elif 'chest' in prompt_lower and ('pain' in prompt_lower or 'pressure' in prompt_lower):
        force_rules = True
        rule_response = "Chest pain or pressure could be a sign of a serious condition like a heart attack. Please seek emergency medical attention immediately by calling emergency services or going to the nearest emergency room. Do not wait to see if the symptoms go away on their own."

    # Common Symptoms - use rules if the threshold is met
    elif use_rules or force_rules:
        # Fever
        if 'fever' in prompt_lower or 'temperature' in prompt_lower:
            rule_response = "If you're experiencing a fever, it's important to stay hydrated and rest. If your temperature is above 102°F (38.9°C) or lasts more than three days, you should consult with your doctor. Over-the-counter medications like acetaminophen or ibuprofen can help reduce fever, but follow dosage instructions carefully."

        # Headache
        elif 'headache' in prompt_lower or 'migraine' in prompt_lower:
            rule_response = "Headaches can be caused by various factors including stress, dehydration, or lack of sleep. Try resting in a dark, quiet room and staying hydrated. Over-the-counter pain relievers may help. If your headache is severe, sudden, or accompanied by other symptoms like fever, stiff neck, or confusion, please seek immediate medical attention as these could be signs of a more serious condition."

        # Respiratory issues
        elif any(symptom in prompt_lower for symptom in ['cough', 'cold', 'flu', 'sore throat', 'congestion', 'runny nose']):
            rule_response = "For respiratory symptoms like coughs, colds, and sore throats, rest and staying hydrated are key. Over-the-counter medications might help with symptoms. Honey can soothe a sore throat (though not for children under 1 year). If you have difficulty breathing, high fever, or symptoms that worsen after 7-10 days, please seek medical attention. Remember to cover coughs and sneezes to prevent spreading illness to others."

        # Digestive issues
        elif any(symptom in prompt_lower for symptom in ['stomach', 'diarrhea', 'vomit', 'nausea', 'constipation', 'indigestion']):
            rule_response = "For digestive issues, try eating bland foods, staying hydrated, and avoiding alcohol, caffeine, and spicy foods. For diarrhea or vomiting, oral rehydration solutions can help replace lost fluids and electrolytes. If symptoms are severe, persistent, or accompanied by high fever or blood in stool/vomit, seek medical attention promptly. Prolonged digestive issues should be evaluated by a healthcare provider."

        # Pain
        elif any(symptom in prompt_lower for symptom in ['pain', 'ache', 'hurt', 'sore']):
            if 'back' in prompt_lower:
                rule_response = "Back pain is common and often improves with rest, gentle stretching, and over-the-counter pain relievers. Apply ice for the first 48-72 hours, then switch to heat. If pain is severe, radiates down your legs, or is accompanied by numbness or weakness, consult a healthcare provider. Maintaining good posture and regular exercise can help prevent future back pain."
            elif 'joint' in prompt_lower or 'arthritis' in prompt_lower:
                rule_response = "Joint pain can be caused by inflammation, injury, or conditions like arthritis. Rest, ice, compression, and elevation (RICE) can help with acute joint pain. Over-the-counter anti-inflammatory medications may provide relief. If joint pain is severe, persistent, or accompanied by significant swelling or inability to use the joint, consult with your healthcare provider."
            else:
                rule_response = "Pain management depends on the cause and location. For minor pain, rest, ice/heat therapy, and over-the-counter pain relievers may help. If pain is severe, persistent, or affecting your daily activities, please consult with a healthcare provider for proper diagnosis and treatment. Chronic pain might require a comprehensive management approach."

        # Sleep issues
        elif any(term in prompt_lower for term in ['sleep', 'insomnia', 'can\'t sleep', 'trouble sleeping', 'tired']):
            rule_response = "Good sleep hygiene can help with sleep issues: maintain a regular sleep schedule, create a restful environment, limit screen time before bed, avoid caffeine and large meals before sleeping, and try relaxation techniques like deep breathing. If sleep problems persist and affect your daily functioning, consider consulting a healthcare provider as it could be related to an underlying condition."

        # Mental health
        elif any(term in prompt_lower for term in ['anxiety', 'stress', 'depression', 'mental health', 'panic', 'worried', 'sad']):
            rule_response = "Mental health is as important as physical health. For managing stress and anxiety, try deep breathing exercises, meditation, physical activity, and maintaining social connections. If you're experiencing persistent feelings of sadness, hopelessness, or anxiety that interfere with daily activities, please reach out to a mental health professional. Remember, seeking help is a sign of strength, not weakness."

        # Nutrition and diet
        elif any(term in prompt_lower for term in ['diet', 'nutrition', 'food', 'eat', 'weight', 'healthy eating']):
            rule_response = "A balanced diet includes a variety of fruits, vegetables, whole grains, lean proteins, and healthy fats. Try to limit processed foods, added sugars, and excessive salt. Stay hydrated by drinking plenty of water. If you have specific dietary needs or are considering a significant diet change, consult with a healthcare provider or registered dietitian for personalized advice."

        # Exercise
        elif any(term in prompt_lower for term in ['exercise', 'workout', 'fitness', 'physical activity']):
            rule_response = "Regular physical activity offers numerous health benefits, including improved mood, better sleep, and reduced risk of chronic diseases. Aim for at least 150 minutes of moderate-intensity exercise per week, along with muscle-strengthening activities twice weekly. Start gradually if you're new to exercise, and choose activities you enjoy to help maintain consistency. Always consult with a healthcare provider before starting a new exercise program, especially if you have existing health conditions."

        # Medication patterns
        elif any(term in prompt_lower for term in ['medication', 'medicine', 'drug', 'prescription', 'pill', 'tablet']):
            rule_response = "I can't provide specific medication advice or prescriptions. Medications should be taken exactly as prescribed by your healthcare provider. Always inform your provider about all medications you're taking, including over-the-counter drugs and supplements, to avoid potential interactions. If you experience side effects or have concerns about your medication, contact your healthcare provider or pharmacist rather than stopping the medication on your own."

        # Appointment patterns
        elif any(term in prompt_lower for term in ['appointment', 'schedule', 'book', 'visit', 'see doctor', 'consultation']):
            rule_response = "To schedule an appointment, you can use the 'Book Appointment' feature in your patient dashboard. Our system allows you to select your preferred doctor, date, and time slot. If you need immediate assistance or have urgent medical concerns, please contact our support team directly. Regular check-ups are an important part of preventive healthcare."

        # Preventive care
        elif any(term in prompt_lower for term in ['prevention', 'preventive', 'check up', 'checkup', 'screening', 'vaccine', 'vaccination', 'immunization']):
            rule_response = "Preventive care is crucial for maintaining good health and detecting potential issues early. This includes regular check-ups, age-appropriate screenings, and vaccinations. Recommended screenings vary based on age, gender, family history, and risk factors. Staying up-to-date with immunizations helps protect against serious diseases. Talk to your healthcare provider about which preventive services are appropriate for you."

        # COVID-19
        elif any(term in prompt_lower for term in ['covid', 'coronavirus', 'pandemic', 'vaccination', 'vaccine']):
            rule_response = "For the most current information about COVID-19, including symptoms, testing, vaccines, and prevention guidelines, please refer to official sources like the CDC or WHO. If you're experiencing symptoms such as fever, cough, or difficulty breathing, please contact your healthcare provider for guidance on testing and care. Follow local public health recommendations regarding masks, social distancing, and other preventive measures."

        # First aid
        elif 'first aid' in prompt_lower or 'emergency' in prompt_lower:
            rule_response = "For medical emergencies, always call emergency services immediately. For minor injuries: clean cuts with soap and water and apply pressure to stop bleeding; run cool water over burns; apply ice wrapped in cloth to sprains or strains. This is general advice only - in serious situations, seek professional medical help right away."

        # Pregnancy
        elif any(term in prompt_lower for term in ['pregnant', 'pregnancy', 'expecting', 'prenatal']):
            rule_response = "Prenatal care is essential during pregnancy. Schedule regular check-ups with your healthcare provider, take prescribed prenatal vitamins, maintain a healthy diet, stay hydrated, and get appropriate exercise. Avoid alcohol, tobacco, and drugs. Contact your healthcare provider immediately if you experience severe abdominal pain, heavy bleeding, severe headaches, or decreased fetal movement. For specific pregnancy concerns, always consult with your healthcare provider."

        # Children's health
        elif any(term in prompt_lower for term in ['child', 'kid', 'baby', 'infant', 'toddler', 'pediatric']):
            rule_response = "Children's healthcare needs differ from adults. Keep up with recommended well-child visits and vaccinations. For infants and young children, watch for signs of dehydration during illness, maintain good nutrition, and ensure adequate sleep. If your child has a high fever, difficulty breathing, unusual rash, or seems unusually lethargic, contact their pediatrician promptly. For specific concerns about your child's health or development, consult with their healthcare provider."

        # Chronic conditions
        elif any(term in prompt_lower for term in ['diabetes', 'hypertension', 'high blood pressure', 'asthma', 'copd', 'heart disease', 'chronic']):
            rule_response = "Managing chronic conditions requires ongoing care and often lifestyle modifications. Take medications as prescribed, keep regular appointments with your healthcare providers, monitor your condition as recommended, and maintain healthy habits. Learn about your condition and recognize warning signs that require medical attention. Support groups can provide valuable information and emotional support. Always consult your healthcare provider for personalized advice about managing your specific condition."

        # Default rule-based responses
        else:
            rule_response = random.choice([
                "I understand you're asking about health matters. Could you provide more details so I can assist you better?",
                "Thank you for your question. To provide accurate information, I'd need more specific details about your concern.",
                "I'm here to help with general health information, but remember that I'm not a substitute for professional medical advice. Please consult with your healthcare provider for personalized guidance.",
                "I'd like to help you with your health question. Could you elaborate a bit more so I can provide relevant information?",
                "For the most accurate advice tailored to your specific situation, it's best to consult with a healthcare professional. I can provide general information if you share more details about your question."
            ])

    # If we're using rule-based response (either by threshold or forced)
    if use_rules or force_rules:
        logger.info(f"Using rule-based response for: {prompt[:30]}...")
        return rule_response

    # Otherwise, use the LLM
    try:
        logger.info(f"Using LLM for response to: {prompt[:30]}...")
        llm_response = llm_service.generate_health_response(enhanced_prompt)

        # Add a disclaimer to LLM responses
        disclaimer = "\n\nRemember, this is general information. Please consult a healthcare professional for personalized advice."

        # Format the response with line breaks
        formatted_response = llm_response.replace(". ", ".\n").replace("! ", "!\n").replace("? ", "?\n")
        
        # Remove any double line breaks that might have been created
        formatted_response = formatted_response.replace("\n\n", "\n")
        
        # Check if response is too long and truncate if necessary
        max_length = 500  # Maximum character length for response
        if len(formatted_response) > max_length:
            formatted_response = formatted_response[:max_length] + "..."

        return formatted_response + disclaimer
    except Exception as e:
        # Log the error and fall back to rule-based response
        logger.error(f"Error using LLM: {str(e)}. Falling back to rule-based response.")

        # Use a generic rule-based response as fallback
        return "I apologize, but I'm having trouble processing your question right now. For health-related questions, it's always best to consult with a healthcare professional for personalized advice. If you have an urgent medical concern, please contact your doctor or emergency services."
