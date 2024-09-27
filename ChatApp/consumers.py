from channels.consumer import AsyncConsumer
from channels.exceptions import StopConsumer
from channels.db import database_sync_to_async
import json
from urllib.parse import parse_qs
from ChatApp.models import *
from django.db.models.signals import post_save
from django.dispatch import receiver    

class MyConsumer(AsyncConsumer):

    instances=set()

    @database_sync_to_async
    def delete_group(self,group_id):
        try:
            group=Groups.objects.get(id=group_id)
            group.delete()
            return "success"
        except Exception as e:
            return str(e)


    @database_sync_to_async
    def get_members(self,group_id):
        group=Groups.objects.get(id=group_id)
        group_members = [{'memberid':member.id,'name':member.Name,'role':member.Role,'reportCount':member.ReportCount,'isOnline':member.isOnline} for member in group.member_set.all()] 
        return group_members
    
    @database_sync_to_async
    def delete_member(self,id):
        try:
            member=Member.objects.get(id=id)
            member.delete()
            return "success"
        except Exception as e:
            return str(e)

    @database_sync_to_async
    def get_member_info(self,id):
        try:
            member=Member.objects.get(id=id)
            group = member.Group
        
            group_name = group.Name
            group_id = group.id
            group_members = [{'memberid':member.id,'name':member.Name,'role':member.Role,'reportCount':member.ReportCount,'isOnline':member.isOnline} for member in group.member_set.all()] 
    
            return {'group_id':group_id,'group_name':group_name,'group_members':group_members,'group_pass':group.Password}
        except Exception as e:
            return {'error':str(e)}
        
    @database_sync_to_async
    def set_status(self,memberid,status):
        try:
            member=Member.objects.get(id=memberid)
            member.isOnline=status
            member.save()
            return {'isOnline':member.isOnline}
        except Exception as e:
            return {'error':str(e)}
    
        
    @database_sync_to_async
    def report_member(self,reportedMember,reportedBy):
        try:
            member=Member.objects.get(id=reportedMember)
            group=member.Group
            reported_by=Member.objects.get(id=reportedBy)
            ReportedBYList=Report.objects.filter(reported_member=member)
            
            for reportedby in ReportedBYList:
            
                if(reportedby.reported_by==reported_by):
                    # print("found")
                    return {'alreadyReported':True,'reportCount':member.ReportCount}
                    
            member.ReportCount+=1
            Report.objects.create(reported_member=member,reported_by=reported_by)
            member.save()
            return {'success':True,'reportCount':member.ReportCount}
            
        except Exception as e:
            return {'error':str(e)}
        
    async def websocket_connect(self,e):
        await self.send({
                'type':'websocket.accept'
        })


        self.group_id=None
        query_param=parse_qs(self.scope['query_string'].decode('utf-8'))
        id=int(query_param.get('id',[None])[0])
       
        member_info=await self.get_member_info(id)
        if(member_info.get("error")):
            await self.send({
                "type":"websocket.send",
                'text':json.dumps({
                    "error":member_info.get("error")
                })
            })
            await self.send({
                "type":"websocket.close"
            })

        else:
            self.group_id=str(member_info['group_id'])
            await self.channel_layer.group_add(self.group_id,self.channel_name)
            self.__class__.instances.add(self)
            await self.channel_layer.group_send(self.group_id,{
                'type':'chat.message',
                'msg':json.dumps({
                    'updateMemberInfo':True,
                    'members':member_info.get('group_members'),
                    'groupName':member_info.get('group_name'),
                    'groupId':member_info.get('group_id'),
                    'groupPass':member_info.get("group_pass"),
                    
                })
            })

    async def websocket_receive(self,e):
        data=json.loads(e['text'])
        print(data)
        
        if(data.get("delete",None)):
            print("Delete request for member id",data.get("memberid"))
            member_info=await self.get_member_info(data.get("memberid"))
            res=await self.delete_member(data.get("memberid"))
            if(res=="success"):
                print("Member Deleted")
                self.group_id=str(member_info.get("group_id")) 
                group_members_updated=await self.get_members(int(self.group_id))
                if(group_members_updated.__len__()==0):
                    # delete group also
                    await self.delete_group(int(self.group_id))    
                    
                await self.channel_layer.group_send(self.group_id,{
                    'type':'chat.message',
                    'msg':json.dumps({
                    'updateMemberInfo':True,
                    'members':group_members_updated,
                    'groupName':member_info.get('group_name'),
                    'groupId':member_info.get('group_id'),
                    
                })
                })
                
                await self.channel_layer.group_discard(self.group_id,self.channel_name)

        elif (data.get('setStatus',None)):
            try:
                memberid=int(data.get('memberid'))
                res=await self.set_status(memberid,data.get('status'))
            except Exception as e:
                pass
            
         
            
        elif (data.get('reportMember',None)):
            reportedMember=data.get('reportMember')
            reportedBy=data.get("reportedBy")
            res=await self.report_member(reportedMember,reportedBy)
            # print(res)
            if(res.get("alreadyReported",None)):
                await self.channel_layer.group_send(self.group_id,{
                    'type':'chat.message',
                    'msg':json.dumps({
                    'alreadyReported':True,
                    'reportCount':res['reportCount'] 
                })
                }) 

            elif(res.get("success",None)):
                await self.channel_layer.group_send(self.group_id,{
                    'type':'chat.message',
                    'msg':json.dumps({
                    'reportedMember':reportedMember,
                    'reportCount':res['reportCount']
                    
                })
                })

            # handel error 
            else :
                pass


        else:
            data['updateMemberInfo']=False
            await self.channel_layer.group_send(self.group_id,{
                'type':'chat.message',
                'msg':json.dumps(data)
            })
            
    async def chat_message(self,e):
        message=e['msg']
        await self.send({
            'type':'websocket.send',
            'text':message,
        })

    async def websocket_disconnect(self,e):
        self.__class__.instances.remove(self)
        if(self.group_id):
            await self.channel_layer.group_discard(self.group_id,self.channel_name)
        raise StopConsumer()
    
    @classmethod
    def get_all_instances(cls):
        return cls.instances



@database_sync_to_async
def get_Group(member):
    group=member.Group
    group_id=str(group.id)
    group_members = [{'memberid':member.id,'name':member.Name,'role':member.Role,'reportCount':member.ReportCount,'isOnline':member.isOnline} for member in group.member_set.all()] 
    
    return {"group_id":group_id,"group_members":group_members}      

@receiver(post_save,sender=Member)
async def update_members(sender,created,**kwargs):
    if not created:
        print("Member Created or Updated")
        group_info=await get_Group(kwargs.get("instance"))
        # print(group_id)
        for instance in MyConsumer.get_all_instances():
            if(instance.group_id==group_info.get("group_id")):  
                # print(instance.group_id)  
                await instance.send({
                    "type":"websocket.send",
                    "text":json.dumps({
                        "updateRequired":True,
                        "members":group_info.get("group_members")
                    })
                })
            else:
                continue
