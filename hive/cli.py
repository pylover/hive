from getpass import getpass

from restfulpy.orm import DBSession
from easycli import SubCommand, Argument

from .models import User


class AddUserSubCommand(SubCommand):
    __command__ = 'add'
    __help__ = 'Add a new user'
    __arguments__ = [
        Argument(
            'name',
            help='Username',
        ),
        Argument(
            'email',
            help='Email address',
        )
    ]

    def __call__(self, args):
        user = User(
            id=args.name,
            email=args.email,
            password=getpass()
        )
        DBSession.add(user)
        DBSession.commit()


class PasswdSubCommand(SubCommand):
    __command__ = 'passwd'
    __help__ = 'change a user\'s password'
    __arguments__ = [
        Argument(
            'name',
            help='Username',
        ),
    ]

    def __call__(self, args):
        user = DBSession.query(User).filter(User.id == args.name).one_or_none()
        if user is None:
            print(f'Invalid username: {args.name}', file=sys.stderr)
            return 1

        password=getpass('New Password:')
        confirm=getpass('Again:')
        if password != confirm:
            print(f'Passwords are mismatch.', file=sys.stderr)
            return 1

        user.password=password
        DBSession.commit()


class UserCommand(SubCommand):
    __command__ = 'user'
    __help__ = 'User administration'
    __arguments__ = [
        AddUserSubCommand,
        PasswdSubCommand,
    ]

