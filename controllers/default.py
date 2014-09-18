# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################
def display():
	c=auth.user_id
	categ=db(db.Category.id>0).select(db.Category.ALL)
	return locals()
	
def categ_display():
	if(len(request.args)>1):
		message=request.args[1]
		response.flash=message
	else:
		response.flash=T("Welcome!")
	if auth.user:
		c1=int(auth.user_id)
	else:
		c1=None
	c=request.args[0]
	news=db(db.Post.Category==c).select(orderby=~(db.Post.ranking))
	return locals()

@auth.requires_login()
def index():
     'auth' in globals()
     if auth.user:
	    c1=auth.user_id 
	    response.flash=T("Welcome to web2py!")
	    if(c1==3):
		    redirect(URL('admin'))
	    else:
		    redirect(URL('client'))
     return locals()
@auth.requires_login()
def admin():
	if(auth.user_id!=3):
		response.flash='access denied'
		redirect(URL('client'))
	'auth' in globals()
	if auth.user:
		return locals()
@auth.requires_login()
def admin_userdel():
	if(auth.user_id!=3):
		response.flash='access denied'
		redirect(URL('client'))
	form=SQLFORM.factory(
			db.Field('Userid','integer',db.auth_user,requires=IS_IN_DB(db,'auth_user.id','auth_user.first_name'),label='Select name'))
	if form.accepts(request.vars,session):
		session.flash='User deleted!'
		redirect(URL(r=request,f='delete_user?id=%d' %int(form.vars.Userid)))
	elif form.errors:
		response.flash='Errors in form'
	return dict(form=form)
	
@auth.requires_login()
def delete_user():
	if(auth.user_id!=3):
		response.flash='access denied'
		redirect(URL('client'))
	userid=int(request.vars.id)
	if(userid==3):
		response.flash='Admin can not be deleted!'
		redirect(URL('admin_userdel'))
	db(db.auth_user.id==userid).delete()
	x=db(db.Like_post.userid==userid).select()
	y=db(db.Dislike.userid==userid).select()
	for i in range(len(x)):
		db(db.Post.id==x[i]['postid']).update(ranking=db.Post.ranking-5)
	for i in range(len(y)):
		db(db.Post.id==y[i]['postid']).update(ranking=db.Post.ranking+3)
	db(db.Like_post.userid==userid).delete()
	db(db.Dislike.userid==userid).delete()
	db(db.Post.userid==userid).delete()
	db(db.Comm.userid==userid).delete()
	return locals()

@auth.requires_login()
def del_post():
	c=int(request.args[0])
	c1=request.args[1]
	db(db.Post.id == c).delete()
	redirect(URL("categ_display/"+c1+"/Postdeleted"))
	return locals()

@auth.requires_login()
def edit_post():
	db.Post.ranking.readable=True
	db.Post.userid.readable=True
	db.Post.ranking.writable=False
	db.Post.userid.writable=False
	db.Post.Category.readable=True
	c=int(request.args[0])
	c1=request.args[1]
	form=SQLFORM(db.Post,c)
	if form.accepts(request.vars,session):
		response.flash='Post updated'
		redirect(URL("categ_display/"+c1+"/Postedited"))
	elif form.errors:
		response.flash='Errors in form'
	return dict(form=form)

@auth.requires_login()
def like_post():
	c2=request.args[1]
	c1=auth.user_id
	c=int(request.args[0])
	db(db.Like_post.postid==c and db.Like_post.userid==c1).delete()
	db(db.Dislike.postid==c and db.Dislike.userid==c1).delete()
	db.Like_post.insert(userid=c1,postid=c)
	x=db(db.Like_post.postid==c).select()
	y=db(c==db.Dislike.postid).select()
	db(db.Post.id==c).update(ranking=100+len(x)*5-len(y)*3)
	redirect(URL("categ_display.html/"+c2+"/liked"))
	return locals()

@auth.requires_login()
def dislike_post():
	c2=request.args[1]
	c1=auth.user_id
	c=int(request.args[0])
	db(db.Like_post.postid==c and db.Like_post.userid==c1).delete()
	db(db.Dislike.postid==c and db.Dislike.userid==c1).delete()
	db.Dislike.insert(userid=c1,postid=c)
	x=db(db.Like_post.postid==c).select()
	y=db(db.Dislike.postid==c).select()
	db(db.Post.id==c).update(ranking=100+len(x)*5-len(y)*3)
	session.flash='Post disliked'
	redirect(URL("categ_display/"+c2+"/disliked"))
	return locals()

@auth.requires_login()

def comm_post():
	c2=request.args[1]
	c1=auth.user_id
	c=int(request.args[0])
	user=db(db.auth_user.id==c1).select(db.auth_user.first_name)
	db.Comm.cdate.default=request.now.date()
	db.Comm.ctime.default=request.now
	comments=db(db.Comm.postid==c).select()
	db.Comm.ctime.readable=False
	db.Comm.ctime.writable=False
	db.Comm.cdate.readable=False
	db.Comm.cdate.writable=False
	db.Comm.userid.readable=False
	db.Comm.userid.writable=False
	db.Comm.postid.readable=False
	db.Comm.postid.writable=False
	db.Comm.userid.default=c1
	db.Comm.postid.default=c
	form=SQLFORM(db.Comm)
	if form.accepts(request.vars,session):
		session.flash='Commented on post!'
		redirect(URL("categ_display/"+c2+"/commented"))
	elif form.errors:
		response.flash('Errors in form')
	return locals()

@auth.requires_login()
def category():
	'auth' in globals()
	if auth.user:
		form=SQLFORM(db.Category)
		if form.process().accepted:
			response.flash='form accepted'
		elif form.errors:
			response.flash='form has errors'
		return dict(form=form)

@auth.requires_login()
def client():
	return locals()

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())
@auth.requires_login()
def post():
	c=auth.user_id
	db.Post.pdate.default=request.now.date()
	db.Post.ptime.default=request.now
	db.Post.userid.default=c
	db.Post.userid.readable=False
	db.Post.userid.writable=False
	db.Post.ptime.readable=False
	db.Post.ptime.writable=False
	db.Post.pdate.readable=False
	db.Post.pdate.writable=False
	db.Post.ranking.default=100
	db.Post.ranking.readable=False
	db.Post.ranking.writable=False
	form=SQLFORM(db.Post)
	if form.process().accepted:
		response.flash='form accepted'
	elif form.errors:
		response.flash='form has errors'
	return locals()

def download():
	return response.download(request, db)


def call():
    """

	db.Post.userid.default=c
	db.Post.userid.readable=False
	db.Post.userid.writable=False
	db.Post.ranking.default=100
	db.Post.ranking.readable=False
	db.Post.ranking.writable=False
	form=SQLFORM(db.Post)
	if form.process().accepted:
		response.flash='form accepted'
	elif form.errors:
		response.flash='form has errors'
	return dict(form=form)
    """

def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())
