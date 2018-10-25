from flask import Flask, request, redirect, render_template, session, flash
import string

def validate_username():
    username_error = ''                            # {0}

    # retrieve form data
    u_candidate = request.form["username"]         # {4}

    # username validation
    if len(u_candidate) == 0:
        username_error = 'Please enter a username.'
    elif ' ' in u_candidate:
        username_error = 'cannot contain spaces.'
    elif len(u_candidate) < 3 or len(u_candidate) > 20:
        username_error = 'must be between 3 and 20 characters.'
    elif u_candidate.isalnum() == False:
        username_error = 'cannot contain special characters.'

    return [u_candidate, username_error]

def validate_password():
    # password validation
    password_error = ''                            # {1}
    p_verification_error = ''                      # {2}

    # retrieve form data
    u_candidate = request.form["username"]
    p_candidate = request.form["password"]
    p_verified = request.form["password_verified"]

    if len(p_candidate) == 0:
        password_error = 'Please enter a password.'
        p_candidate = ''
        p_verified = ''
    elif ' ' in p_candidate:
        password_error = 'cannot contain spaces.'
        p_candidate = ''
        p_verified = ''
    elif len(p_candidate) < 8 or len(p_candidate) > 20:
        password_error = 'must be between 8 and 20 characters.'
        p_candidate = ''
        p_verified = ''
    elif u_candidate in p_candidate or p_candidate in u_candidate:
        password_error = 'should not be similar to usernames.'
        p_candidate = ''
        p_verified = ''
    # password matching validation
    if p_candidate != p_verified:
        p_verification_error = 'Passwords do not match.'
        p_candidate = ''
        p_verified = ''

    return [p_candidate, password_error, p_verification_error]

def validate_email():
    # email validation
    email_error = ''                               # {3}

    # retrieve form data
    e_candidate = request.form["email"]            # {5}

    if e_candidate == '':
        email_error = ''
        e_candidate = None
    elif ' ' in e_candidate:
        email_error = 'cannot contain spaces.'
    elif len(e_candidate) < 3 or len(e_candidate) > 254:
        email_error = 'must be between 3 and 254 characters.'
    elif e_candidate.count("@") != 1:
        email_error = 'must contain 1 "@" symbol.'
    elif e_candidate.count(".") < 1:
        email_error = 'must contain at least 1 "." symbol.'

    return [e_candidate, email_error]

def signup_validation():
    u_validation = validate_username()
    p_validation = validate_password()
    e_validation = validate_email()

    u_candidate = u_validation[0]
    p_candidate = p_validation[0]
    e_candidate = e_validation[0]

    u_error = u_validation[1]
    p_error = p_validation[1]
    pv_error = p_validation[2]
    e_error = e_validation[1]

    u_confirmed = ''
    p_confirmed = ''
    e_confirmed = ''

    valid = True

    # validate username
    if len(u_error) == 0:
        u_confirmed = u_candidate
    else:
        valid = False

    # validate password
    if len(p_error + pv_error) == 0:
        p_confirmed = p_candidate
    else:
        valid = False

    # validate email
    if len(e_error) == 0:
        e_confirmed = e_candidate
    else:
        valid = False

    # if valid, pass confirmed variables
    # if not valid, pass candidates with errors
    if valid == True:
        return [u_confirmed, p_confirmed, e_confirmed]
    else:
        return [u_error, p_error, pv_error, e_error, u_candidate, e_candidate]
