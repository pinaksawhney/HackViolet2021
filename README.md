# HackViolet2021

APIs:

LOGIN page
1. login(username, password, fb_login, google_login): POST  
	return : if logged in {"success": true}
		 else {"success": false}

	either usrname + password or fb_login or google_login

2. sign up(username, password,email id) : POST
	return : if account created {"success": true}
		 else {"success": false}


HOME page
3. get_tutorial(search_string)	: GET
	return {"coursera": "url here", "edx": "url here", "khan_academcy": "url here, .... ... }

4. get_history()		: GET
	return {"coursera": "url here", "edx": "url here", "khan_academcy": "url here, .... ... }


MEETUP

5. get_meetups(search_string, location, date)	:  GET
	return {"meet up1", "meet up2", "meet up3"}

SUPPORT GROUP

6. join_room(chat_room_id) POST
	return : if logged in {"success": true}
		 else {"success": false}

7. send_message(msg, chat_room_id): POST
	return : if logged in {"success": true}
		 else {"success": false}

8. get_message(chat_room_id)	GET
	return : if logged in {"success": true}
		 else {"success": false}

RESOURCES

9. get_resources(category): GET
	return {"Technology": ["GHC", "AnitaBorg"], "Lifeskill": ["Masterclass", "SkillUp"], .... ... }
