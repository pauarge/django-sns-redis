# Django SNS Redis

## Welcome!

Welcome to Django SNS Redis! This package lets you send push notifications right from your [Django](https://www.djangoproject.com) project using [Amazon's](https://aws.amazon.com) [Simple Notification Service](https://aws.amazon.com/sns/). The cool thing about it is that is has a built-in [Redis](http://redis.io) cache for storing devices' ARNs (specially usefull when you have tons of users and don't wanna squeeze your relational database).

## How it works
Django SNS Redis allows you to register devices with their registration_id provided by GCM/APNS. Then, it stores it to a database and obtains an ARN from SNS. 

Since that ARN is associated to a user and stored in Redis, when publishing a message, you won't hit the database. That, added to the features SNS provides, will help your app deliver notifications much faster and with less resources.

## Requirements
The library might work with versions prior to the ones specified, but they are not tested. Feel free to submit a pull request if you have tested other versions (or if you have patched the library!).

* [Python](https://www.python.org/) (2.7+)
* [Django](https://www.djangoproject.com/) (1.8+)
* [Django Redis](https://github.com/niwinz/django-redis) (4.3+)
* [Boto](https://github.com/boto/boto) (2.42+)

## Setup
Add the following to your Django settings file (usually, settings.py):

~~~~
INSTALLED_APPS = [..., snsredis, ...]

AWS_ACCESS_KEY_ID = [your key id]
AWS_SECRET_ACCESS_KEY = [your secret]
AWS_REGION_NAME = [region where you have the desired SNS instances]

AWS_SNS_APNS_ARN = [ARN for your iOS app]
AWS_SNS_GCM_ARN = [ARN for your Android app]
~~~~

What are we doing there?

First, we are adding the library to your Django project installed apps. This is necessary for the rest of the project to *talk* to the library.

Then we are adding some keys that Amazon will provide you.

* **ACCESS KEY ID** and **SECRET ACCESS KEY** is a pair of keys that let you use your AWS resources from outside. You can set up them [here](https://console.aws.amazon.com/iam/home). Make sure your keys have permissions to operate SNS.

* **REGION NAME** is the region in which you have configured your SNS instances.

* **SNS APNS/GCM ARN** (ARN stands for Amazon Resource Name). IDs of the SNS applications (you can register them [here](https://eu-west-1.console.aws.amazon.com/sns/v2/home)). This parameters are only required for the platforms you want to use.

**Remember to apply migrations!**

## Usage

### Adding a user token

~~~~
from django.contrib.auth.models import User
from snsredis.tasks import add_token

user = User.objects.get(id=1)
registration_id = 'xxxxxxxxx'
platform = 'gcm'

add_token(user, registration_id, platform)

~~~~

### Publishing a message

~~~~
from django.contrib.auth.models import User
from snsredis.tasks import publish

user = User.objects.get(id=1)
message = 'Hello world'
extra = {
			'post': 123,
			'url': 'http://www.example.com'
		}
sound = 'default.mp3'

publish(user, message, extra, sound)

~~~~

### Removing user token

~~~~
from django.contrib.auth.models import User
from snsredis.tasks import remove_token

user = User.objects.get(id=1)
registration_id = 'xxxxxxxxx'

remove_token(user, registration_id)

~~~~