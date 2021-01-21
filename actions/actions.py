# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction
from rasa_sdk.events import AllSlotsReset, EventType
from actions.third_weather import get_weather_now, get_weather_three_days, get_weather_by_day
import datetime

# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []


class AskForSlotAction(Action):
    def name(self) -> Text:
        return "action_ask_slot"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        if not (tracker.get_slot("address") and tracker.get_slot("date_time")):
            dispatcher.utter_message("请同时包含完整的地址和时间(仅可查询未来三天的天气)哟！")
        else:
            dispatcher.utter_message("好的，现在帮你查询...")
        return []

class WeatherForm(FormAction):
    def name(self) -> Text:
        """Unique identifier of the form"""

        return "weather_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""

        return ["date_time", "address"]

    def submit(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict]:
        """Define what the form has to do
            after all required slots are filled"""
        address = tracker.get_slot('address')
        date_time = tracker.get_slot('date_time')

        date_time_number = text_date_to_number_date(date_time)

        if isinstance(date_time_number, str):  # parse date_time failed
            dispatcher.utter_message("暂不支持查询 {} 的天气".format(address+date_time_number))
        elif date_time_number == -1:
            weather_data = get_weather_now(address)
            message = "{}当前温度{}℃，当前体感温度{}℃，实况天气{}，实况风向{}，实况风力等级{}级，实况风速{}公里/小时，" \
                      "实况相对湿度{}，实况降水量{}mm，实况能见度{}公里".format(address,
                                                            weather_data['temp'],
                                                            weather_data['feelsLike'],
                                                            weather_data['text'],
                                                            weather_data['windDir'],
                                                            weather_data['windScale'],
                                                            weather_data['windSpeed'],
                                                            weather_data['humidity'],
                                                            weather_data['precip'],
                                                            weather_data['vis'])
            dispatcher.utter_message(message)
        else:
            weather_data = get_weather_data(date_time_number, address)
            message = "{} 最高温度：{}℃，最低温度：{}℃，白天天气状况{}，夜间天气状况{}".format(address+date_time,
                                                                      weather_data['tempMax'],
                                                                      weather_data['tempMin'],
                                                                      weather_data['textDay'],
                                                                      weather_data['textNight'])
            dispatcher.utter_message(message)
        return [AllSlotsReset()]

def get_weather_data(number, address):
    if number == -1:
        res = get_weather_now(address)
    else:
        date = datetime.datetime.now()
        date = date + datetime.timedelta(days=number)
        res = get_weather_by_day(address, date)
    return res



# 转换为Number方便判断不支持查询的情况
def text_date_to_number_date(text_date):
    if text_date == "现在":
        return -1
    if text_date == "今天":
        return 0
    if text_date == "明天":
        return 1
    if text_date == "后天":
        return 2

    # Not supported by weather API provider freely
    if text_date == "大后天":
        # return string
        return text_date

    if text_date.startswith("星期"):
        # @todo: using calender to compute relative date
        return text_date

    if text_date.startswith("下星期"):
        # @todo: using calender to compute relative date
        return text_date

    # follow APIs are not supported by weather API provider freely
    if text_date == "昨天":
        return text_date
    if text_date == "前天":
        return text_date
    if text_date == "大前天":
        return text_date





