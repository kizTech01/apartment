from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from apartments.models import Apartment, InteractionLog
from accounts.models import User
from notifications.services import notify
from .forms import MessageForm
from .models import Message

@login_required
def start(request, apartment_pk):
    apartment = get_object_or_404(Apartment, pk=apartment_pk, status=Apartment.Status.AVAILABLE)
    if request.user == apartment.landlord or request.user.role != "TENANT": raise Http404
    return redirect("messaging:thread", apartment_pk=apartment.pk, other_pk=apartment.landlord.pk)

@login_required
def thread(request, apartment_pk, other_pk):
    apartment = get_object_or_404(Apartment, pk=apartment_pk)
    other = get_object_or_404(User, pk=other_pk)
    # A conversation is permitted only between this apartment's owner and a tenant.
    if request.user == apartment.landlord:
        if other.role != User.Role.TENANT: raise Http404
    elif request.user.role == User.Role.TENANT:
        if other != apartment.landlord: raise Http404
    else:
        raise Http404
    conversation = Message.objects.filter(apartment=apartment).filter(Q(sender=request.user, receiver=other) | Q(sender=other, receiver=request.user)).select_related("sender")
    conversation.filter(receiver=request.user, is_read=False).update(is_read=True)
    form = MessageForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        msg = form.save(commit=False); msg.sender = request.user; msg.receiver = other; msg.apartment = apartment; msg.save()
        if request.user.role == "TENANT": InteractionLog.objects.create(tenant=request.user, apartment=apartment, action=InteractionLog.Action.MESSAGE)
        notify(other, "New apartment message", f"{request.user.full_name} sent you a message about {apartment.title}.", "MESSAGE", request.path)
        return redirect(request.path)
    return render(request, "messaging/thread.html", {"apartment": apartment, "other": other, "conversation": conversation, "form": form})

@login_required
def inbox(request):
    messages_qs = Message.objects.filter(Q(sender=request.user) | Q(receiver=request.user)).select_related("apartment", "sender", "receiver").order_by("-timestamp")
    seen, threads = set(), []
    for message in messages_qs:
        other = message.receiver if message.sender_id == request.user.id else message.sender
        key = (message.apartment_id, other.id)
        if key not in seen: seen.add(key); threads.append((message, other))
    return render(request, "messaging/inbox.html", {"threads": threads})
