import os
import uuid
from django.db import models
from django.forms import ValidationError
from train_station import settings
from django.utils.text import slugify

class TrainType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return f"{self.name}"


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

def train_image_file_path(instance, filename):
    _, extencion = os.path.splitext(filename)
    filename = f"{slugify(instance.name)}-{uuid.uuid4()}{extencion}"
    return os.path.join("uploads/trains", filename)



class Train(models.Model):
    name = models.CharField(max_length=255, unique=True)
    cargo_num = models.IntegerField()
    places_in_cargo = models.IntegerField()
    train_type = models.ForeignKey(TrainType, on_delete=models.CASCADE)
    image = models.ImageField(null=True, upload_to=train_image_file_path)
    
    @property
    def capacity(self) -> int:
        return self.cargo_num * self.places_in_cargo
    
    def __str__(self) -> str:
        return f"{self.name}"




class Station(models.Model):
    name = models.CharField(max_length=255, unique=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    
    def __str__(self):
        return self.name


class Route(models.Model):
    source = models.ForeignKey(Station, on_delete=models.CASCADE, related_name="route_src")
    destination = models.ForeignKey(Station, on_delete=models.CASCADE, related_name="route_dest")
    distance = models.IntegerField()
    
    @property
    def full_route(self) -> str:
        return f"{self.source.name} - {self.destination.name}"

    def __str__(self) -> str:
        return self.full_route

class Journey(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    train = models.ForeignKey(Train, on_delete=models.CASCADE)
    crew = models.ManyToManyField(Crew)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    
    def __str__(self):
        return f"{self.route}: {self.departure_time}"


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    
    class Meta:
        ordering = ["-created_at"]


class Ticket(models.Model):
    cargo = models.IntegerField()
    seat = models.IntegerField()
    journey = models.ForeignKey(Journey,
                                on_delete=models.CASCADE,
                                related_name="tickets")
    order = models.ForeignKey(Order,
                              on_delete=models.CASCADE,
                              related_name="tickets")

    def __str__(self):
        return f"{self.journey} cargo: {self.cargo}, seat: {self.seat}"

    @staticmethod
    def validate_ticket(cargo, seat, journey, error_to_rise):
        for ticket_attr_value, ticket_attr_name, journey_attr_name in [
            (cargo, "cargo_num", "cargo_num"),
            (seat, "places_in_cargo", "places_in_cargo"),
        ]:
            count_attrs = getattr(journey, journey_attr_name)
            if not (1 <= ticket_attr_value <= count_attrs):
                raise error_to_rise(
                    {
                        ticket_attr_name: f"{ticket_attr_name} "
                        f"number must be in avaliable range: "
                        f"(1, {journey_attr_name}): "
                        f"(1, {count_attrs})"
                    }
                )
    def clean(self):
        Ticket.validate_ticket(
            self.cargo,
            self.seat,
            self.journey.train,
            ValidationError,
        )
    
    def save(self,
             force_insert = False,
             force_update = False,
             using = None,
             update_fields = None):
        self.full_clean()
        return super(Ticket, self).save(
            force_insert,
            force_update,
            using,
            update_fields
        )
    
    class Meta:
        unique_together = ("journey", "cargo", "seat")
