from django.contrib import admin
from station.models import (TrainType,
                            Train,
                            Order,
                            Station,
                            Ticket,
                            Crew,
                            Journey,
                            Route)

admin.site.register(TrainType)
admin.site.register(Train)
admin.site.register(Order)
admin.site.register(Station)
admin.site.register(Ticket)
admin.site.register(Crew)
admin.site.register(Journey)
admin.site.register(Route)
