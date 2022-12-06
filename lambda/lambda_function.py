# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import ask_sdk_core.utils as ask_utils
import json
import re
import requests
from datetime import datetime
import time
import pytz

import pandas as pd
import numpy as np
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.utils import get_supported_interfaces
from ask_sdk_model.interfaces.alexa.presentation.apl import (
    RenderDocumentDirective,
    ExecuteCommandsDirective,
    SpeakItemCommand,
    AutoPageCommand,
    HighlightMode,
)

from difflib import SequenceMatcher
from ask_sdk_model import Response
from utils import sync_questions, sync_readings, f,check_similarity

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

API_URL1 = 'http://demo.wakeb.tech/swcc-text-to-voice/public'
API_URL = 'http://demo.wakeb.tech/swcc-text-to-voice/public/api/questions/data'
API_TOKEN = 'PYFleLjukIJZ1G22hvhdNwx3eidkauxqLQUvoQXzBSmiQDWGCb6yv3RhCjvhikjr'
API_URL2 = 'http://demo.wakeb.tech/swcc-text-to-voice/public/api/questions/stock'
#data = sync_readings(API_URL, API_TOKEN)
data = pd.read_csv("data.csv")
data2 = sync_readings(API_URL2, API_TOKEN)
question_and_answer = {"question": "", "answer": []}
list_ = data["toal_water_production"].unique().tolist()
list_1 = data["phase"].unique().tolist()
list_day = data['day'].unique().tolist()
list_day_2 = data2['day'].unique().tolist()
new_list_ = []
new_list_phase = []
new_list_day = []
new_list_day2 = []

for i in range(len(list_day)):
    # list_day[i] = re.sub('\W+','', list_day[i])
    if i < 9:
        x = list_day[i].replace("0","")
        x = x[::-1]
        x = x.replace("222","2022")
        new_list_day.append(re.sub("\W+", "", x))
        continue
    x = f(list_day[i])
    x = x.replace("02220","2022")
    new_list_day.append(re.sub("\W+", "", x))

for i in range(len(list_day_2)):
    # list_day[i] = re.sub('\W+','', list_day[i])
    if i < 9:
        x = list_day_2[i].replace("0","")
        x = x[::-1]
        x = x.replace("222","2022")
        new_list_day2.append(re.sub("\W+", "", x))
        continue
    x = f(list_day_2[i])
    x = x.replace("02220","2022")
    new_list_day2.append(re.sub("\W+", "", x))    
    
    
for i in range(len(list_1)):
    new_list_phase.append(re.sub(r"[^A-Za-z0-9]", "", list_1[i]))

for i in range(len(list_)):
    if i < 9:
        new_list_.append(list_[i].replace("0", ""))
        continue
    new_list_.append(re.sub(r"[^A-Za-z0-9]", "", list_[i]))


def _load_apl_document(file_path):
    ## type: (str) -> Dict[str, Any]
    """Load the apl json document at the path into a dict object."""
    with open(file_path) as f:
        return json.load(f)


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        
        locale = handler_input.request_envelope.request.locale
        #accesstoken = str(handler_input.request_envelope.context.system.api_access_token)
        #endpoint = "https://api.amazonalexa.com/v2/persons/~current/profile/name"
        #api_access_token = "Bearer " + accesstoken
        #headers = {"Authorization": api_access_token}
        #r = requests.get(endpoint, headers=headers)
        #name = r.json()
        
        # t = requests.get("https://api.amazonalexa.com/v2/persons/~current/profile/personId", headers=headers)
        # print("-------------",name)
        # print(t.content)
        # speak_output = name
        if locale == "en-US":
            #speak_output = "Welcome " + name + ", you can say Hello or Help. Which would you like to try?"
            speak_output = "Welcome"
        elif locale == "ar-SA":
            #speak_output = "مرحبا "+str(name)
            #speak_output = "مَرْحَبًا " + name + " كَيْفَ يُمْكِنُنِي مُسَاعَدَتَكَ؟"
            # speak_output = "سوك"
            speak_output = "هلا"
        
        
        #if type(name) != str:
        #    quit()
            
        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )


class HelloWorldIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("HelloWorldIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Hello World!"

        return (
            handler_input.response_builder.speak(speak_output)
            # .ask("add a reprompt if you want to keep the session open for the user to respond")
            .response
        )


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "You can say hello to me! How can I help?"

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.CancelIntent")(
            handler_input
        ) or ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        locale = handler_input.request_envelope.request.locale
        if locale == "ar-SA":
            speak_output = "يرعاك الله"
        else:
            speak_output = "Goodbye!"

        return handler_input.response_builder.speak(speak_output).response


class FallbackIntentHandler(AbstractRequestHandler):
    """Single handler for Fallback Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        locale = handler_input.request_envelope.request.locale

        # type: (HandlerInput) -> Response
        logger.info("In FallbackIntentHandler")

        if locale == "ar-SA":
            speech = "أَنَا لَسْتُ مُتَأَكِّدَةً مَاذَا تُرِيدُ"
            reprompt = "أَنَا لَمْ أَتَمَكَّنْ مِنْ ذَلِكَ كَيْفَ أُسَاعِدُكُ"
        else:
            speech = "Hmm, I'm not sure. You can say Hello or Help. What would you like to do?"
            reprompt = "I didn't catch that. What can I help you with?"
        
        return  handler_input.response_builder.speak(speech).ask(reprompt).response

class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class InfoRequestIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("info")(handler_input)

    def handle(self, handler_input):
        speak_output = "I am here to help you, monitoring the realtime issues."

        question_and_answer["question"] = "Ask about information"
        question_and_answer["answer"] = []
        question_and_answer["answer"].append(speak_output)
        sync_questions(API_URL1, API_TOKEN, question_and_answer)

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )


class generaldateRequestIntentHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("generaldate")(handler_input)
    
    def handle(self, handler_input):
        speak_output = 'today is, '+datetime.now().strftime("%B %d, %Y")
        
        question_and_answer["question"] = "Ask about date"
        question_and_answer['answer'] = []
        question_and_answer['answer'].append(speak_output)
        sync_questions(API_URL1, API_TOKEN, question_and_answer)
        
        
        return (
           handler_input.response_builder.speak(speak_output).ask(speak_output).response
        )    

class info_arabicIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("info_arabic")(handler_input)

    def handle(self, handler_input):
        # slots = handler_input.request_envelope.request.intent.slots
        # foodtype = slots['foodtype'].value

        # if foodtype == "orange" or foodtype == "appel":
        #   speak_outputdd = ["yes, we offer orange","yes, we offer appel"]
        #  speak_output = '  '.join(speak_outputdd)
        # else:
        # speak_output = str(data.shape)
        speak_output = "أَنَا هُنَا لِمُسَاعَدَتِكَ فِي مُتَابَعَةِ اَلْمَشَاكِلِ لَحْظَةً بِلَحْظَةٍ."

        question_and_answer["question"] = "Ask about information about swcc"
        question_and_answer["answer"] = []
        question_and_answer["answer"].append(speak_output)
        sync_questions(API_URL1, API_TOKEN, question_and_answer)

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )

class units_problemsIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("units_problems")(handler_input)

    def handle(self, handler_input):
        # slots = handler_input.request_envelope.request.intent.slots
        # foodtype = slots['foodtype'].value

        # if foodtype == "orange" or foodtype == "appel":
        #   speak_outputdd = ["yes, we offer orange","yes, we offer appel"]
        #  speak_output = '  '.join(speak_outputdd)
        # else:
        # speak_output = str(data.shape)
        list_speak = []
        list_speak.append( "اَلتَّنْبِيهَات اَلْيَوْمِ هِيَ")
        df = data[data["day"] == "2022-05-31"]

        for i in range(len(df)):
            if df["value"].iloc[i] < 50:
                issue = ("وَحْدَةٌ "+ df["toal_water_production"].iloc[i] + " لَدَيْهَا مُشْكِلَةٌ فِي يَوْمٍ "+ "واحد و ثلاثون خمسة ألفان  و اثنان و عشرون")
                list_speak.append(issue)    
        speak_output = ", ".join(list_speak)
        question_and_answer["question"] = "Ask about problems about swcc"
        question_and_answer["answer"] = []
        question_and_answer["answer"].append(speak_output)
        sync_questions(API_URL1, API_TOKEN, question_and_answer)
        
        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )

class unit_problem_englishIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("unit_problem_english")(handler_input)

    def handle(self, handler_input):
        # slots = handler_input.request_envelope.request.intent.slots
        # foodtype = slots['foodtype'].value

        # if foodtype == "orange" or foodtype == "appel":
        #   speak_outputdd = ["yes, we offer orange","yes, we offer appel"]
        #  speak_output = '  '.join(speak_outputdd)
        # else:
        # speak_output = str(data.shape)
        list_speak = []
        list_speak.append("the alerts are ")
        df = data[data["day"] == "2022-05-31"]
        print(df.columns)
        for i in range(len(df)):
            if df["value"].iloc[i] < 50:
                #issue = ("وَحْدَةٌ "+ df["toal_water_production"].iloc[i] + " لَدَيْهَا مُشْكِلَةٌ فِي يَوْمٍ "+ "واحد و ثلاثون خمسة ألفان  و اثنان و عشرون")
                issue = "unit " + df['toal_water_production'].iloc[i] + "has a problem in " + " 2022-05-31 "
                list_speak.append(issue)    
        speak_output = ", ".join(list_speak)
        question_and_answer["question"] = "Ask about problems about swcc"
        question_and_answer["answer"] = []
        question_and_answer["answer"].append(speak_output)
        sync_questions(API_URL1, API_TOKEN, question_and_answer)
        
        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )


class thanks_arabicRequestIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("thanks_arabic")(handler_input)

    def handle(self, handler_input):

        speak_output = "عَفْوًا ، سُوِيك دَائِمًا فِي خِدْمَتِكُمْ"
        # speak_output = "انا swick مساعدك الذكى طورت بواسطة واكب"

        question_and_answer["question"] = "Ask about thanks"
        question_and_answer["answer"] = []
        question_and_answer["answer"].append(speak_output)
        sync_questions(API_URL1, API_TOKEN, question_and_answer)

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )


class dashboardarabicRequestIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("dashboard_arabic")(handler_input)

    def handle(self, handler_input):
        speak_output = "تم فتح الموقع"

        if get_supported_interfaces(handler_input).alexa_presentation_apl is not None:

            question_and_answer["question"] = "Ask about the dashboard"
            question_and_answer["answer"] = []
            question_and_answer["answer"].append(speak_output)
            sync_questions(API_URL, API_TOKEN, question_and_answer)
            return (
                handler_input.response_builder.speak(speak_output)
                .ask("A reprompt to keep the session open")
                .add_directive(
                    RenderDocumentDirective(
                        token="pagerToken",
                        document=_load_apl_document("open.json"),
                        datasources={},
                    )
                )
                .response
            )

        else:
            speak_output = "يوجد خطأ للوصول للموقع"
            question_and_answer["question"] = "Ask about the dashboard"
            question_and_answer["answer"] = []
            question_and_answer["answer"].append(speak_output)
            sync_questions(API_URL1, API_TOKEN, question_and_answer)
            return (
                handler_input.response_builder.speak(speak_output)
                .ask("Please buy an Alexa device with a screen")
                .response
            )


class dashboardRequestIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("dashboard")(handler_input)

    def handle(self, handler_input):
        speak_output = "the dashboard opend now"

        if get_supported_interfaces(handler_input).alexa_presentation_apl is not None:

            question_and_answer["question"] = "Ask about the dashboard"
            question_and_answer["answer"] = []
            question_and_answer["answer"].append(speak_output)
            sync_questions(API_URL, API_TOKEN, question_and_answer)
            return (
                handler_input.response_builder.speak(speak_output)
                .ask("A reprompt to keep the session open")
                .add_directive(
                    RenderDocumentDirective(
                        token="pagerToken",
                        document=_load_apl_document("open.json"),
                        datasources={},
                    )
                )
                .response
            )

        else:
            speak_output = "You don't have a screen"
            question_and_answer["question"] = "Ask about the dashboard"
            question_and_answer["answer"] = []
            question_and_answer["answer"].append(speak_output)
            sync_questions(API_URL1, API_TOKEN, question_and_answer)
            return (
                handler_input.response_builder.speak(speak_output)
                .ask("Please buy an Alexa device with a screen")
                .response
            )


class GreetingRequestIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("greetings")(handler_input)

    def handle(self, handler_input):
        speak_output = "I'm fine, thanks"

        question_and_answer["question"] = "Ask about greeting"
        question_and_answer["answer"] = []
        question_and_answer["answer"].append(speak_output)
        sync_questions(API_URL, API_TOKEN, question_and_answer)

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )


class num_areasRequestIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("num_areas")(handler_input)

    def handle(self, handler_input):

        number_of_areas = len(data['toal_water_production'][data['plant']=="Al-Jubail"].unique())
        speak_output = "there are " + str(number_of_areas) + " found"

        question_and_answer["question"] = "Ask about number of units"
        question_and_answer["answer"] = []
        question_and_answer["answer"].append(speak_output)
        sync_questions(API_URL1, API_TOKEN, question_and_answer)

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )


class num_areas_arabicRequestIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("num_areas_arabic")(handler_input)

    def handle(self, handler_input):

        number_of_areas = len(data['toal_water_production'][data['plant']=="Al-Jubail"].unique())
        speak_output = "يُوجَدُ " + str(number_of_areas) + " وَحْدَةٌ"

        question_and_answer["question"] = "Ask about number of units"
        question_and_answer["answer"] = []
        question_and_answer["answer"].append(speak_output)
        sync_questions(API_URL1, API_TOKEN, question_and_answer)

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )


class num_of_enterpriseRequestIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("num_of_enterprise")(handler_input)

    def handle(self, handler_input):

        total_enterprise = str(32)
        speak_output = "the total production of the enterprise is " + str(
            total_enterprise
        )

        question_and_answer["question"] = "Ask about the total production enterprise"
        question_and_answer["answer"] = []
        question_and_answer["answer"].append(speak_output)
        sync_questions(API_URL1, API_TOKEN, question_and_answer)

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )


class num_of_enterprise_arabicRequestIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("num_of_enterprise_arabic")(handler_input)

    def handle(self, handler_input):

        total_enterprise = str(32)
        speak_output = "عَدَدُ اَلْمَنْظُومَاتِ اَلْكُلِّيِّ " + str(total_enterprise)

        question_and_answer["question"] = "Ask about the total production enterprise"
        question_and_answer["answer"] = []
        question_and_answer["answer"].append(speak_output)
        sync_questions(API_URL1, API_TOKEN, question_and_answer)

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )


class greetings_arabicRequestIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("greetings_arabic")(handler_input)

    def handle(self, handler_input):

        speak_output = "حياك الله"

        question_and_answer["question"] = "Ask about greetings"
        question_and_answer["answer"] = []
        question_and_answer["answer"].append(speak_output)
        sync_questions(API_URL1, API_TOKEN, question_and_answer)

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )


class swcc_arabicRequestIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("swcc_arabic")(handler_input)

    def handle(self, handler_input):

        speak_output = (
                "أَنَا سُوِيك، مُسَاعِدُكَ اَلذَّكِيُّ"        )
        # speak_output = "انا swick مساعدك الذكى طورت بواسطة واكب"

        question_and_answer["question"] = "Ask about swcc"
        question_and_answer["answer"] = []
        question_and_answer["answer"].append(speak_output)
        sync_questions(API_URL1, API_TOKEN, question_and_answer)

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )


class stage_gabelenglishRequestIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("stage_gabel_english")(handler_input)

    def handle(self, handler_input):
        number_of_phases = len(data['phase'].unique())
        speak_output = (
            "The Jubail system consists of " + str(number_of_phases) + " phases"
        )
        # speak_output = "انا swick مساعدك الذكى طورت بواسطة واكب"

        question_and_answer["question"] = "Ask about stages"
        question_and_answer["answer"] = []
        question_and_answer["answer"].append(speak_output)
        sync_questions(API_URL1, API_TOKEN, question_and_answer)

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )


class specific_unit_problemenglishRequestIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("specific_unit_problem")(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        unit = slots["new_stage"].value
        unit = re.sub(r"[^A-Za-z0-9]", "", unit)
        #print("======================", unit)
        list_speak = []
        index = check_similarity(unit, new_list_)
        for i in list_day:
            value = data['value'][(data['day'] == i) & (data['toal_water_production'] == list_[index])].values[0]
            #value = value.replace("٬", "")
            if int(value) < 50:
         #       print("========================", index)
                list_speak.append(list_[index]+ " unit has problem in day "+ i+ " and the production is "+ str(value))
        speak_output = ", ".join(list_speak)
        # speak_output = "انا swick مساعدك الذكى طورت بواسطة واكب"

        question_and_answer["question"] = "Ask about stages"
        question_and_answer["answer"] = []
        question_and_answer["answer"] = list_speak
        sync_questions(API_URL1, API_TOKEN, question_and_answer)

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )

class specific_unit_problem_arabicRequestIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("specific_unit_problem_arabic")(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        unit = slots["unitp"].value
        unit = re.sub(r"[^A-Za-z0-9]", "", unit)
        #print("======================", unit)
        list_speak = []
        index = check_similarity(unit, new_list_)
        for i in list_day:
            value = data['value'][(data['day'] == i) & (data['toal_water_production'] == list_[index])].values[0]
            #value = value.replace("٬", "")
            if int(value) < 50:
                #print("========================", index)
                list_speak.append("وَحْدَة " + list_[index] + " لَدَيْهَا مُشْكِلَةٌ فِي يَوْمٍ " + i + " وَالْإِنْتَاجُ هُوَ " + str(value))
        speak_output = ", ".join(list_speak)
        # speak_output = "انا swick مساعدك الذكى طورت بواسطة واكب"

        question_and_answer["question"] = "Ask about stages"
        question_and_answer["answer"] = []
        question_and_answer["answer"] = list_speak
        sync_questions(API_URL1, API_TOKEN, question_and_answer)

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )


class number_of_out_unitsenglishRequestIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("number_of_out_units")(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        dayy = slots["new_day"].value
        dayy = re.sub(r"[^A-Za-z0-9]", "", dayy)
        index = check_similarity(dayy, new_list_day)
        counter = len(data[(data['value'] < 50) & (data['day']==list_day[index])])
        speak_output = "the number of failure units are " + str(counter)
        # speak_output = "انا swick مساعدك الذكى طورت بواسطة واكب"

        question_and_answer["question"] = "Ask about failure units"
        question_and_answer["answer"] = []
        question_and_answer["answer"].append(speak_output)
        sync_questions(API_URL1, API_TOKEN, question_and_answer)

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
    
        )
        
class num_of_in_units_arabicRequestIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("num_of_in_units_arabic")(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        dayy = slots["dayf"].value
        dayy = re.sub(r"[^A-Za-z0-9]", "", dayy)
        index = check_similarity(dayy, new_list_day)
        counter = len(data[(data['value'] >= 50) & (data['day']==list_day[index])])
        speak_output = "عَدَدُ اَلْوَحَدَاتِ اَلدَّاخِلِ فِي اَلْخِدْمَةِ " + str(counter)   

        question_and_answer["question"] = "Ask about failure units"
        question_and_answer["answer"] = []
        question_and_answer["answer"].append(speak_output)
        sync_questions(API_URL1, API_TOKEN, question_and_answer)

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )        
        
class number_of_out_units_arabicRequestIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("number_of_out_units_arabic")(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        dayy = slots["dayc"].value
        dayy = re.sub(r"[^A-Za-z0-9]", "", dayy)
        index = check_similarity(dayy, new_list_day)
        counter = len(data[(data['value'] < 50) & (data['day']==list_day[index])])
        speak_output = "عَدَدُ اَلْوَحَدَاتِ اَلْخَارِجَةِ عَنْ اَلْخِدْمَةِ " + str(counter)
        # speak_output = "انا swick مساعدك الذكى طورت بواسطة واكب"

        question_and_answer["question"] = "Ask about failure units"
        question_and_answer["answer"] = []
        question_and_answer["answer"].append(speak_output)
        sync_questions(API_URL1, API_TOKEN, question_and_answer)

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )        
        
class power_production_arabicRequestIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("power_production")(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        dayy = slots["dayu"].value
        dayy = re.sub(r"[^A-Za-z0-9]", "", dayy)
        index = check_similarity(dayy, new_list_day2)
        counter = data2['power'][(data2['day'] == list_day_2[index]) & (data2['plant'] == "Jubail")].tolist()[0]
        speak_output = "نِسْبَة تَوْلِيدِ اَلْكَهْرَبَاءِ هِيَ " + str(counter) + " كيلو وات "

        question_and_answer["question"] = "Ask about power production"
        question_and_answer["answer"] = []
        question_and_answer["answer"].append(speak_output)
        sync_questions(API_URL1, API_TOKEN, question_and_answer)

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )      
        
class power_production_englishRequestIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("power_production_english")(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        dayy = slots["dayp"].value
        dayy = re.sub(r"[^A-Za-z0-9]", "", dayy)
        index = check_similarity(dayy, new_list_day2)
        counter = data2['power'][(data2['day'] == list_day_2[index]) & (data2['plant'] == "Jubail")].tolist()[0]
        speak_output = "the power production is " + str(counter)
        question_and_answer["question"] = "Ask about power production"
        question_and_answer["answer"] = []
        question_and_answer["answer"].append(speak_output)
        sync_questions(API_URL1, API_TOKEN, question_and_answer)

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )         
        

class water_stock_arabicRequestIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("water_stock_arabic")(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        dayy = slots["dayp"].value
        dayy = re.sub(r"[^A-Za-z0-9]", "", dayy)
        index = check_similarity(dayy, new_list_day2)
        counter = data2['stock'][(data2['day'] == list_day_2[index]) & (data2['plant'] == "Jubail")].tolist()[0]
        speak_output = "نِسْبَة اَلْخَزْنِ هِيَ " + str(counter) + " متر مكعب "
        question_and_answer["question"] = "Ask about water stock"
        question_and_answer["answer"] = []
        question_and_answer["answer"].append(speak_output)
        sync_questions(API_URL1, API_TOKEN, question_and_answer)

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        ) 
        
class stock_water_englishRequestIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("stock_water_english")(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        dayy = slots["dayt"].value
        dayy = re.sub(r"[^A-Za-z0-9]", "", dayy)
        index = check_similarity(dayy, new_list_day2)
        counter = data2['stock'][(data2['day'] == list_day_2[index]) & (data2['plant'] == "Jubail")].tolist()[0]
        speak_output = "the water stock is " + str(counter)
        question_and_answer["question"] = "Ask about water stock"
        question_and_answer["answer"] = []
        question_and_answer["answer"].append(speak_output)
        sync_questions(API_URL1, API_TOKEN, question_and_answer)

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )         
        

class actual_export_arabicRequestIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("actual_export_arabic")(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        dayy = slots["dayh"].value
        dayy = re.sub(r"[^A-Za-z0-9]", "", dayy)
        index = check_similarity(dayy, new_list_day2)
        counter = data2['export'][(data2['day'] == list_day_2[index]) & (data2['plant'] == "Jubail")].tolist()[0]
        speak_output = "إِجْمَالِيُّ اَلتَّصْدِيرِ هُوَ " + str(counter)
        question_and_answer["question"] = "Ask about actual export"
        question_and_answer["answer"] = []
        question_and_answer["answer"].append(speak_output)
        sync_questions(API_URL1, API_TOKEN, question_and_answer)

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        ) 
        
class actual_export_englishRequestIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("actual_export_english")(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        dayy = slots["dayl"].value
        dayy = re.sub(r"[^A-Za-z0-9]", "", dayy)
        index = check_similarity(dayy, new_list_day2)
        counter = data2['export'][(data2['day'] == list_day_2[index]) & (data2['plant'] == "Jubail")].tolist()[0]
        speak_output = "the actual export is " + str(counter)
        question_and_answer["question"] = "Ask about actual export"
        question_and_answer["answer"] = []
        question_and_answer["answer"].append(speak_output)
        sync_questions(API_URL1, API_TOKEN, question_and_answer)

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )         


class num_areas_per_stagenglishRequestIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("num_areas_per_stage")(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        stage = slots["stagex"].value
        stage = re.sub(r"[^A-Za-z0-9]", "", stage)
        index = check_similarity(stage, new_list_phase)
        speak_output = "عَدَدُ اَلْوَحَدَاتِ فِي مَرْحَلَةٍ " + str(len(data['toal_water_production'][data['phase']==list_1[index]].unique())) + " وَحَدَاتٌ"      

        question_and_answer["question"] = "Ask about number of units in specific stage"
        question_and_answer["answer"] = []
        question_and_answer["answer"].append(speak_output)
        sync_questions(API_URL1, API_TOKEN, question_and_answer)

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )


class num_of_units_per_stageRequestIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("num_of_units_per_stage")(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        stage = slots["stagep"].value
        stage = re.sub(r"[^A-Za-z0-9]", "", stage)
        index = check_similarity(stage, new_list_phase)
        speak_output = "the number of units in " + list_1[index] + " is " + str(len(data['toal_water_production'][data['phase']==list_1[index]].unique()))
        question_and_answer["question"] = "Ask about number of units in specific stage"
        question_and_answer["answer"] = []
        question_and_answer["answer"].append(speak_output)
        sync_questions(API_URL1, API_TOKEN, question_and_answer)

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )

class stage_gabelarabicRequestIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("stage_gabel_arabic")(handler_input)

    def handle(self, handler_input):
        number_of_phases = len(data['phase'].unique())
        speak_output = (
            "مَنْظُومَة اَلْجُبَيْلْ تَتَكَوَّنُ مِنْ "
            + str(number_of_phases)
            + " مَرَاحِلُ"
        )
        question_and_answer["question"] = "Ask about stages"
        question_and_answer["answer"] = []
        question_and_answer["answer"].append(speak_output)
        sync_questions(API_URL1, API_TOKEN, question_and_answer)

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )


class restartRequestIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("restart")(handler_input)

    def handle(self, handler_input):
        # data['value'] = [np.random.uniform(row[['ll']].values[0]/1.009, row[['hh']].values[0]*1.009) for row in data.iloc]
        # data['status'] = ['Abnormal' if row.value >= row.hh or row.value < row.ll else 'Normal' for row in data.iloc]
        # speak_output = "OK, I am capturing the realtime systems readings."
        # data = sync_readings(API_URL, API_TOKEN)
        data = sync_readings(API_URL, API_TOKEN)
        data2 = sync_readings(API_URL2, API_TOKEN)

        speak_output = "OK, I am capturing the realtime systems readings."

        question_and_answer["question"] = "Ask about restart system"
        question_and_answer["answer"] = []
        question_and_answer["answer"].append(speak_output)
        sync_questions(API_URL1, API_TOKEN, question_and_answer)
        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )


class restart_arabicRequestIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("restart_arabic")(handler_input)

    def handle(self, handler_input):
        data = sync_readings(API_URL, API_TOKEN)
        data2 = sync_readings(API_URL2, API_TOKEN)
        # data = sync_readings(API_URL, API_TOKEN)
        # data = pd.read_csv("sheet_new.csv")
        speak_output = (
            "حَسَنًا ، أَقُومُ اَلْآنُ بِقِرَاءَةِ وَتَحْدِيثِ اَلْأَخْطَاءِ."
        )

        question_and_answer["question"] = "Ask about restart system"
        question_and_answer["answer"] = []
        question_and_answer["answer"].append(speak_output)
        sync_questions(API_URL, API_TOKEN, question_and_answer)

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )


class specific_stageenglishRequestIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("specific_stage_month")(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        phase = slots["stage"].value
        phase = re.sub(r"[^A-Za-z0-9]", "", phase)
        # s.replace('٬', '')
        #if phase == "":
        #    phase = "RO"
        index = check_similarity(phase, new_list_phase)
        print(list_1[index])
        total_per_month = sum(data['value'][data['phase']==list_1[index]].tolist())
        #total_per_month = total_per_month.replace("٬", "")
        speak_output = "The total production for " + list_1[index] + " is " + str(total_per_month)
        # speak_output = "انا swick مساعدك الذكى طورت بواسطة واكب"

        question_and_answer[
            "question"
        ] = "Ask about total production for specific phase"
        question_and_answer["answer"] = []
        question_and_answer["answer"].append(speak_output)
        sync_questions(API_URL1, API_TOKEN, question_and_answer)

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )


class specific_stage_month_arabicRequestIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("specific_stage_month_arabic")(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        phase = slots["stage"].value
        phase = re.sub(r"[^A-Za-z0-9]", "", phase)
        #if phase == "":
        #    phase = "RO"
        index = check_similarity(phase, new_list_phase)
        total_per_month = sum(data['value'][data['phase']==list_1[index]].tolist())
        total_per_month = str(total_per_month)
        #total_per_month = total_per_month.replace("٬", "")
        speak_output = (
            "كَمِّيَّة اَلْإِنْتَاجِ فِي " + list_1[index] + " " + total_per_month
        )
        # speak_output = "انا swick مساعدك الذكى طورت بواسطة واكب"

        question_and_answer[
            "question"
        ] = "Ask about total production for specific phase"
        question_and_answer["answer"] = []
        question_and_answer["answer"].append(speak_output)
        sync_questions(API_URL1, API_TOKEN, question_and_answer)

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )


class gabil_quatity_per_stageRequestIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("gabil_quatity_per_area_month")(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        area = slots["new_stage"].value
        area = re.sub(r"[^A-Za-z0-9]", "", area)
        index = check_similarity(area, new_list_)
        print("index", index)
        print("area",area)
        total_per_month = sum(data['value'][data['toal_water_production']==list_[index]].tolist())
        #total_per_month = total_per_month.replace("٬", "")
        speak_output = "The total production for " + list_[index] + " is " + str(total_per_month)
        # speak_output = "انا swick مساعدك الذكى طورت بواسطة واكب"

        question_and_answer["question"] = "Ask about total production for specific unit"
        question_and_answer["answer"] = []
        question_and_answer["answer"].append(speak_output)
        sync_questions(API_URL1, API_TOKEN, question_and_answer)

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )


class unit_per_day_englishRequestIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("unit_per_day_english")(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        area = slots["new_unit"].value
        day = slots["day"].value
        area = re.sub(r"[^A-Za-z0-9]", "", area)
        day = re.sub(r"[^A-Za-z0-9]", "", day)
        index1 = check_similarity(area, new_list_)
        index2 = check_similarity(day, new_list_day)
        total_per_day = data['value'][(data['day'] == list_day[index2]) & (data['toal_water_production'] == list_[index1])].values[0]
        speak_output = "The total production for this unit is " + str(total_per_day)
        # speak_output = "انا swick مساعدك الذكى طورت بواسطة واكب"

        question_and_answer[
            "question"
        ] = "Ask about The total production in specific day"
        question_and_answer["answer"] = []
        question_and_answer["answer"].append(speak_output)
        sync_questions(API_URL1, API_TOKEN, question_and_answer)

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )

class unit_per_day_arabicRequestIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("unit_per_day_arabic")(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        area = slots["unitm"].value
        day = slots["dayr"].value
        area = re.sub(r"[^A-Za-z0-9]", "", area)
        day = re.sub(r"[^A-Za-z0-9]", "", day)
        index1 = check_similarity(area, new_list_)
        index2 = check_similarity(day, new_list_day)
        total_per_day = data['value'][(data['day'] == list_day[index2]) & (data['toal_water_production'] == list_[index1])].values[0]
        speak_output = "كَمِّيَّة اَلْإِنْتَاجِ هِيَ " + str(total_per_day)
        # speak_output = "انا swick مساعدك الذكى طورت بواسطة واكب"

        question_and_answer[
            "question"
        ] = "Ask about The total production in specific day"
        question_and_answer["answer"] = []
        question_and_answer["answer"].append(speak_output)
        sync_questions(API_URL1, API_TOKEN, question_and_answer)

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )


class generaltimeRequestIntentHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("generaltime")(handler_input)
    
    def handle(self, handler_input):
        tz = pytz.timezone('Asia/Riyadh')
        speak_output = 'time is, '+datetime.now(tz).strftime("%H:%M:%S")
        
        question_and_answer["question"] = "Ask about time"
        question_and_answer['answer'] = []
        question_and_answer['answer'].append(speak_output)
        sync_questions(API_URL1, API_TOKEN, question_and_answer)
        
        return (
           handler_input.response_builder.speak(speak_output).ask(speak_output).response
        )
        
class time_arabicRequestIntentHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("time_arabic")(handler_input)
    
    def handle(self, handler_input):
        
        tz = pytz.timezone('Asia/Riyadh')
        speak_output = 'اَلتَّوْقِيت اَلْآنِ, '+datetime.now(tz).strftime("%I:%M %p")
        question_and_answer["question"] = "Ask about time"
        question_and_answer['answer'] = []
        question_and_answer['answer'].append(speak_output)
        sync_questions(API_URL1, API_TOKEN, question_and_answer)

       
        return (
           handler_input.response_builder.speak(speak_output).ask(speak_output).response
        )         

class specific_area_in_day_arabicRequestIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("specific_area_in_day")(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        area = slots["area_q"].value
        day = slots["day_q"].value
        area = re.sub(r"[^A-Za-z0-9]", "", area)
        day = re.sub(r"[^A-Za-z0-9]", "", day)
        index1 = check_similarity(area, new_list_)
        index2 = check_similarity(day, new_list_day)
        total_per_day = data['value'][(data['day'] == list_day[index2]) & (data['toal_water_production'] == list_[index1])].values[0]
        total_per_day = str(total_per_day)
        speak_output = "كَمِّيَّة اَلْإِنْتَاجِ فِي " + list_[index] + " " + total_pe_day
        # speak_output = "انا swick مساعدك الذكى طورت بواسطة واكب"

        question_and_answer[
            "question"
        ] = "Ask about The total production in specific day"
        question_and_answer["answer"] = []
        question_and_answer["answer"].append(speak_output)
        sync_questions(API_URL1, API_TOKEN, question_and_answer)

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )

class gabil_quatity_per_area_month_arabicRequestIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("gabil_quatity_per_area_month_arabic")(
            handler_input
        )

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        area = slots["new_stage"].value
        area = re.sub(r"[^A-Za-z0-9]", "", area)
        index = check_similarity(area, new_list_)
        total_per_month = sum(data['value'][data['toal_water_production']==list_[index]].tolist())
        #total_per_month = total_per_month.replace("٬", "")
        total_per_month = str(total_per_month)
        speak_output = (
            "كَمِّيَّة اَلْإِنْتَاجِ فِي " + list_[index] + " " + total_per_month
        )
        # speak_output = "انا swick مساعدك الذكى طورت بواسطة واكب"

        question_and_answer[
            "question"
        ] = "Ask about The total production for unit in month"
        question_and_answer["answer"] = []
        question_and_answer["answer"].append(speak_output)
        sync_questions(API_URL1, API_TOKEN, question_and_answer)

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )


class informationRequestIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("information")(handler_input)

    def handle(self, handler_input):
        speak_output = "I am Swick, your AI virtual assistant"

        question_and_answer["question"] = "Ask about information about swcc"
        question_and_answer["answer"] = []
        question_and_answer["answer"].append(speak_output)
        sync_questions(API_URL1, API_TOKEN, question_and_answer)
        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )


class date_arabicRequestIntentHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("date_arabic")(handler_input)
    
    def handle(self, handler_input):
        speak_output = 'اليوم هو, '+datetime.now().strftime("%B %d, %Y")
        
        question_and_answer["question"] = "Ask about date"
        question_and_answer['answer'] = []
        question_and_answer['answer'].append(speak_output)
        sync_questions(API_URL1, API_TOKEN, question_and_answer)

        
        return (
           handler_input.response_builder.speak(speak_output).ask(speak_output).response
        )    
        

class gabel_production_quatityRequestIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("gabel_production_quatity")(handler_input)

    def handle(self, handler_input):
        all_production = sum(data['value'][data['plant']=="Al-Jubail"].tolist())

        speak_output = "the total production for jubail is " + str(all_production)
        question_and_answer[
            "question"
        ] = "Ask about The total production for jubail system"
        question_and_answer["answer"] = []
        question_and_answer["answer"].append(speak_output)
        sync_questions(API_URL1, API_TOKEN, question_and_answer)
        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )


class gabel_production_quatity_arabicRequestIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("gabel_production_quatity_arabic")(
            handler_input
        )

    def handle(self, handler_input):
        all_production = sum(data['value'][data['plant']=="Al-Jubail"].tolist())
        speak_output = "اَلْإِنْتَاج اَلْكُلِّيِّ لِمَنْظُومَةِ اَلْجُبَيْلْ " + str(
            all_production
        )
        question_and_answer[
            "question"
        ] = "Ask about The total production for jubail system"
        question_and_answer["answer"] = []
        question_and_answer["answer"].append(speak_output)
        sync_questions(API_URL1, API_TOKEN, question_and_answer)
        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder.speak(speak_output)
            # .ask("add a reprompt if you want to keep the session open for the user to respond")
            .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """

    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        locale = handler_input.request_envelope.request.locale
        logger.error(exception, exc_info=True)

        if locale == "ar-SA":
            speak_output = "لَا أَسْتَطِيعُ أَنْ أُفِيدَكُ حَاوَلَ مَرَّةً أُخْرَى"
        else:
            speak_output = (
                "Sorry, I had trouble doing what you asked. Please try again."
            )

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )


# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(HelloWorldIntentHandler())
sb.add_request_handler(HelpIntentHandler())

sb.add_request_handler(stage_gabelenglishRequestIntentHandler())

sb.add_request_handler(info_arabicIntentHandler())

sb.add_request_handler(thanks_arabicRequestIntentHandler())

sb.add_request_handler(greetings_arabicRequestIntentHandler())

sb.add_request_handler(stage_gabelarabicRequestIntentHandler())

sb.add_request_handler(swcc_arabicRequestIntentHandler())

sb.add_request_handler(specific_stage_month_arabicRequestIntentHandler())

sb.add_request_handler(specific_unit_problemenglishRequestIntentHandler())
sb.add_request_handler(num_areasRequestIntentHandler())

sb.add_request_handler(dashboardarabicRequestIntentHandler())

sb.add_request_handler(gabil_quatity_per_area_month_arabicRequestIntentHandler())
sb.add_request_handler(num_of_enterprise_arabicRequestIntentHandler())

sb.add_request_handler(gabil_quatity_per_stageRequestIntentHandler())

sb.add_request_handler(number_of_out_units_arabicRequestIntentHandler())

sb.add_request_handler(unit_per_day_englishRequestIntentHandler())

sb.add_request_handler(unit_per_day_arabicRequestIntentHandler())

sb.add_request_handler(number_of_out_unitsenglishRequestIntentHandler())
sb.add_request_handler(generaltimeRequestIntentHandler())

sb.add_request_handler(num_of_in_units_arabicRequestIntentHandler())

sb.add_request_handler(num_of_units_per_stageRequestIntentHandler())

sb.add_request_handler(water_stock_arabicRequestIntentHandler())
sb.add_request_handler(actual_export_arabicRequestIntentHandler())


sb.add_request_handler(specific_unit_problem_arabicRequestIntentHandler())

sb.add_request_handler(actual_export_englishRequestIntentHandler())
sb.add_request_handler(stock_water_englishRequestIntentHandler())
sb.add_request_handler(power_production_englishRequestIntentHandler())

sb.add_request_handler(restart_arabicRequestIntentHandler())



sb.add_request_handler(time_arabicRequestIntentHandler())

sb.add_request_handler(num_of_enterpriseRequestIntentHandler())

sb.add_request_handler(units_problemsIntentHandler())
sb.add_request_handler(generaldateRequestIntentHandler())

sb.add_request_handler(power_production_arabicRequestIntentHandler())
sb.add_request_handler(date_arabicRequestIntentHandler())

sb.add_request_handler(num_areas_per_stagenglishRequestIntentHandler())
sb.add_request_handler(gabel_production_quatity_arabicRequestIntentHandler())

sb.add_request_handler(unit_problem_englishIntentHandler())

sb.add_request_handler(gabel_production_quatityRequestIntentHandler())

sb.add_request_handler(num_areas_arabicRequestIntentHandler())
sb.add_request_handler(specific_area_in_day_arabicRequestIntentHandler())

sb.add_request_handler(dashboardRequestIntentHandler())
sb.add_request_handler(restartRequestIntentHandler())
sb.add_request_handler(specific_stageenglishRequestIntentHandler())
sb.add_request_handler(InfoRequestIntentHandler())
sb.add_request_handler(informationRequestIntentHandler())
sb.add_request_handler(GreetingRequestIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(
    IntentReflectorHandler()
)  # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
