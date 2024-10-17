# MyFirstWebApp
### Video Demo:  <https://youtu.be/4NuHJSN2YIY>
### Description:
The project is a help desk application, designed mainly for internal use at the company where I work, which has many limitations in terms of employees who are often people with little computer agility and need something simple for ticket management.
It serves to manage support tickets and facilitate solutions to problems raised by users.

#### It had a few iterations:
1. It was just supposed to be a site to save important links for the IT role, like server IPs, or switches or software portals that we installed internally.
2. Then it evolved to also be a file sharing system, with file upload and download.
3. And finally the ticket management application

#### Build on:
The application is built using HTML, CSS, JavaScript for the frontend
Backend uses Flask, a Python framework combined with Jinja.
I trie to ensure a blend of modern web development practices, making the site responsive, scalable for different resolutions with mobile in mind also.

#### Design:
One key aspect that i tried to implement was the minimalistic design with corporate branding colors.
The interface is simple to use and the simple layout and design ensure quick and intuitive access to the help desk’s features.
Logo (its a own made logo, not the company's real logo)
It have few buttons, theme button, profile and logout, when user is logged in and register and loggin when the user is logged out.
When user is logged in the button of "Tickets", "Solutions" and "User" appear depending on the role of the user.

#### Functionality:
In terms of functionality, the help desk system revolves around a structured user-role hierarchy, ensuring that each individual interacts with the platform according to their responsibilities.

The three user roles are:

#### Admin: Responsible for managing all aspects of the help desk.
- Admins can respond to tickets raised by users
- Manage other users by changing their role, or deleting accounts, reset passwords and create comprehensive solutions for recurring problems.
- Accept new users (waiting for admin aproval)
- They have an overview of all ongoing issues.

#### Power User: Has permissions that focus more on customer support rather than administration.
- They can respond to tickets
- Ability to create new solutions
- This role are restricted, can not do user administration
- This role is designed for users that may not need administrative control but are crucial in resolving insues and building a knowledge base.

#### User: Regular users, submitting tickets.
- They can create tickets
- Once their issue is resolved, they have the ability to archive or check as unresolved their ticket for future reference
- Users can also access solutions created by admins or power users, allowing them to independently troubleshoot common problems without needing to wait for assistance.
- They are restricted from creating solutions themselves, making the role purely for ticket submission and consumption of existing help resources.

#### Features the app also have:
- Themes
    - light and dark
- email notifications
	- User
        - Confirmation of the registration, waiting for aproval
        - Registration aproved by admin
        - ticket status changed, terminated
    - admin
        - New user
	    - New ticket submited
    - Reset password
    Implemented a system of onetime password when password is reseted by the admin or forgeted by the user
- Email verification at registration
- password with min 8 chars
- Profile update
    - change name
    - change password

#### Database:
The database is basically structured in 4 tables, users, tickets, solutions and messages, to store all the information needed for the HelpDesk application.
It has a table to link tickets and solutions to connect them, since many solutions can be referenced in a single ticket.