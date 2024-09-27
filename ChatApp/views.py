from django.shortcuts import render
from django.http import JsonResponse
from ChatApp.models import *
from django.views.decorators.csrf import csrf_exempt
import json
import hashlib


# Create your views here.

def make_hash(password):
    encoded_pass=password.encode()
    sha256_hash=hashlib.sha256()
    sha256_hash.update(encoded_pass)
    hashed_pass=sha256_hash.hexdigest()
    return hashed_pass

def chat(req):
    if(req.method=="GET"):
        try:
            return render(req,"chat.html")
        except Exception as e:
            return JsonResponse({"error":str(e)})
    

@csrf_exempt
def home(req):
    if(req.method=="POST"):
        try:
            json_data=json.loads(req.body.decode('utf-8'))
            username=json_data.get('username')
            password=json_data.get("password")
            # print(password)
            
            if(json_data.get("createGroup")):
                group_name=json_data.get('groupName')
                group_limit=int(json_data.get('groupLimit'))
                Group=Groups.objects.create(Name=group_name,Limit=group_limit,Password=make_hash(password))
                member=Member.objects.create(Name=username,Group=Group,Role="admin")
                return JsonResponse({'memberid':member.id},status=200)
            else:
                group_id=int(json_data.get("groupId"))
                group=Groups.objects.get(id=group_id)
                share_mode=bool(json_data.get("sharemode"))
                print(share_mode)

                if(share_mode):
                    if(password!=group.Password):
                        return JsonResponse({'error':"Your Link Is Broken !!"},status=400)  
                else:
                    if(make_hash(password)!=group.Password):
                        return JsonResponse({'error':"Incorrect Password !!"},status=400)
                
                current_group_members=group.member_set.all().__len__()
                # print(current_group_members)
                if(current_group_members>=group.Limit):
                    return JsonResponse({'error':"The group has already reached its maximum number of members"},status=400)
                for member in group.member_set.all():
                    if(str(member.Name).lower().strip()==str(username).lower().strip()):
                        return JsonResponse({"error":"Username Already Exist !!"},status=400)
                member=Member.objects.create(Name=username.strip(),Group=group)
                return JsonResponse({'memberid':member.id},status=200)
        except Exception as e:
            return JsonResponse({'error':str(e)},status=400)
    else:
        return render(req,'index.html')
    




