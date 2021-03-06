# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

import logging


def index():
    """
    This is the main page of the wiki.
    You will find the title of the requested page in request.args(0).
    If this is None, then just serve the latest revision of something titled "Main page" or something
    like that.
    """
    title = request.args(0) or 'main page'
    display_title = title.title()
    title=title.replace (" ", "_")
    logger.info("This is a request for page %r" %
         (title))
    logger.info("type of request.client %r" %
            (type(request.client)))
    #if title!='main page' or len(request.args) != 0 :
    if db(db.pagetable.title==title).select().first() is None:
            redirect(URL('default', 'create',args=[title]))

    page_id = db(db.pagetable.title == title).select().first().id

    rev = db(db.revision.pagetable_id == page_id).select(orderby=~db.revision.created_on).first()


    s = rev.body if rev is not None else ''

    editing = request.vars.edit == 'y'

    if editing:
        # We are editing.  Gets the body s of the page.
        # Creates a form to edit the content s, with s as default.
        auth.basic()
        """if auth.user==None:
            session.currenttitle=title
            redirect(URL('default', 'user'))"""


        form = SQLFORM.factory(Field('comment','text',label='revision comment'),
                                  Field('body', 'text',
                                     label='Content',
                                     default=s
                                     ))
        # You can easily add extra buttons to forms.
        form.add_button('Cancel', URL('default', 'index',args=[title]))
        form.add_button('History', URL('default', 'history',args=[title]))


        # Processes the form.
        if form.process().accepted:
            # Writes the new content.
            """if rev is None:
                # First time: we need to insert it.
                #db.revision.insert(body=form.vars.body)
                db.revision.insert(body=form.vars.body)
            else:
                # We update it.
                rev.update_record(body=form.vars.body)"""
            auth.basic()
            if auth.user==None:
                db.revision.insert(pagetable_id=page_id,body=form.vars.body,
                                  created_by=auth.user_id,user_ip=request.client,
                                  logged=False,revision_comment=form.vars.comment)
            else:
                db.revision.insert(pagetable_id=page_id,body=form.vars.body,
                                  created_by=auth.user_id,user_ip=request.client,
                                  logged=True,revision_comment=form.vars.comment)



            redirect(URL('default', 'index',args=[title]))
        content = form
    else:
        # We are just displaying the page
        content = s

    return dict(display_title=display_title,title=title,
                 content=content,editing=editing)

@auth.requires_login()
def create():
    title = request.args(0)
    form = SQLFORM.factory(Field('body', 'text',
                                 label='Content'
                                 ))
    form.add_button('Cancel', URL('default', 'index'))
    if form.process().accepted:
        db.pagetable.insert(title=title)
        page_id = db(db.pagetable.title == title).select().first().id
        db.revision.insert(body=form.vars.body,pagetable_id=page_id,
        revision_comment='initialization')
        redirect(URL('default', 'index',args=[title]))
    content = form
    return dict(display_title=title.title(),content=content)

def history():
    title=request.args(0)
    logger.info("This is a request for page %r" %
         (title))
    auth.basic()
    if request.vars.rev=='y':
        post=db(db.revision.id==request.vars.post_id).select().first()
        logger.info("request.vars.rev= %r" %
             (request.vars.rev))
        logger.info("type of post in history()  %r" %
             (type(post)))
        logger.info("request.vars.post_id  %r" %
             (request.vars.post_id))
        logger.info("post.created_on  %r" %
             (post.created_on))
        logger.info("type of post.created_on  %r" %
                (type(post.created_on)))
        revision_comment='Revert to '+str(post.created_on)
        if auth.user==None:
             logged=False
        else:
             logged=True
        db.revision.insert(pagetable_id=post.pagetable_id,body=post.body,
                          created_by=auth.user_id,user_ip=request.client,
                          logged=logged,revision_comment=revision_comment)
        redirect(URL('default', 'index',args=[title]))

    page_id = db(db.pagetable.title == title).select().first().id
    posts = db(db.revision.pagetable_id == page_id).select(orderby=~db.revision.created_on)

    """logger.info("posts type %r" %
         (type(posts)))"""
    return  dict(posts=posts,title=title)

def test():
    """This controller is here for testing purposes only.
    Feel free to leave it in, but don't make it part of your wiki.
    """
    title = "This is the wiki's test page"
    form = None
    content = None

    # Let's uppernice the title.  The last 'title()' below
    # is actually a Python function, if you are wondering.
    display_title = title.title()

    # Gets the body s of the page.
    r = db.testpage(1)
    s = r.body if r is not None else ''
    # Are we editing?
    editing = request.vars.edit == 'true'
    # This is how you can use logging, very useful.
    logger.info("This is a request for page %r, with editing %r" %
                 (title, editing))
    if editing:
        # We are editing.  Gets the body s of the page.
        # Creates a form to edit the content s, with s as default.
        form = SQLFORM.factory(Field('body', 'text',
                                     label='Content',
                                     default=s
                                     ))
        # You can easily add extra buttons to forms.
        form.add_button('Cancel', URL('default', 'test'))
        # Processes the form.
        if form.process().accepted:
            # Writes the new content.
            if r is None:
                # First time: we need to insert it.
                db.testpage.insert(id=1, body=form.vars.body)
            else:
                # We update it.
                r.update_record(body=form.vars.body)
            # We redirect here, so we get this page with GET rather than POST,
            # and we go out of edit mode.
            redirect(URL('default', 'test'))
        content = form
    else:
        # We are just displaying the page
        content = s
    return dict(display_title=display_title, content=content, editing=editing)


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    session.flash=T('Not authorized Please log in')
    auth.settings.login_next = URL('default', 'index',args=[session.currenttitle])
    return dict(form=auth())


@cache.action()
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


@auth.requires_login()
def api():
    """
    this is example of API with access control
    WEB2PY provides Hypermedia API (Collection+JSON) Experimental
    """
    from gluon.contrib.hypermedia import Collection
    rules = {
        '<tablename>': {'GET':{},'POST':{},'PUT':{},'DELETE':{}},
        }
    return Collection(db).process(request,response,rules)
