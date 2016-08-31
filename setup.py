from distutils.core import setup

setup(
    name='django-sns-redis',
    version='0.1.3',
    packages=['snsredis',],
    license='MIT License',
    description='Simple package for sending push notifications through AWS SNS using Django and Redis',
    long_description=open('README.md').read(),
)
