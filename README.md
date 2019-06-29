

Test task for user registration with email confirmation and invitation codes.

First, check up SingUpForm - it creates inactive user and sends email.
I encrypted invitation codes and user id to token (using itsdangerous package)

Then, confirm_email view decrypt user id and invitation codes from token,
it activates user and creates profile for him.

Points scoring and token generation logic I putted to Profile model.
Also created Profile Detail and List views according to the task.

I did not put much efford to frontend and email sending.
(because it is a backend position, and for emails project probably needs another app)

Please, provide some feedback
