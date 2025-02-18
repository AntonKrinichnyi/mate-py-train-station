from datetime import datetime
import tempfile
import os
from PIL import Image
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse
from station.models import Train, Journey, Route, Crew, TrainType, Station
from station.serializers import JourneyListSerializer, TrainListSerializer, TrainDetailSerializer

TRAIN_URL = reverse("station:train-list")
JOURNEY_URL = reverse("station:journey-list")

def sample_train_type(**params):
    defaults = {
        "name": "Sample train type",
    }
    defaults.update(params)
    
    return TrainType.objects.create(**defaults)

def sample_train(**params):
    train_type = sample_train_type()
    defaults =  {
        "name": "Sample train",
        "train_type": train_type,
        "cargo_num": 10,
        "places_in_cargo": 60,
    }
    defaults.update(params)
    
    return Train.objects.create(**defaults)

def sample_journey(**params):
    source = Station.objects.create(
        name="Sample source station",
        latitude=777.555,
        longitude=666.444,
    )
    destination = Station.objects.create(
        name="Sample destination station",
        latitude=12.35,
        longitude=66.44,
    )
    route = Route.objects.create(
        source=source,
        destination=destination,
        distance=200
    )
    train = sample_train()
    defaults = {
        "route": route,
        "train": train,
        "departure_time": datetime(2025, 2, 26, 10),
        "arrival_time": datetime(2025, 2, 27, 1)
    }
    defaults.update(params)
    return Journey.objects.create(**defaults)

def image_upload_url(train_id):
    return reverse("station:train-upload-image", args=[train_id])

def detail_url(train_id):
    return reverse("station:train-detail", args=[train_id])

class UnautheticatedStationApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
    
    def test_auth_required(self):
        res = self.client.get(TRAIN_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedStationApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create(
            "sample@test.com",
            "samplepass4334",
        )
        self.client.force_authenticate(self.user)
    
    def test_train_list(self):
        sample_train()
        sample_train()
        res = self.client.get(TRAIN_URL)
        trains = Train.objects.order_by("id")
        serializer = TrainListSerializer(trains, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
    
    def test_filter_journey_by_daparture_time(self):
        journey1 = sample_journey(departure_time=datetime(2025, 2, 3, 10))
        journey2 = sample_journey(departure_time=datetime(2025, 1, 5, 9))
        date_sample = "2025-02-03"
        res = self.client.get(
            JOURNEY_URL, {"departure_date": "date_sample"}
        )
        serializer1 = JourneyListSerializer(journey1)
        serializer2 = JourneyListSerializer(journey2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)
    
    def test_create_train_forbidden(self):
        train_type = TrainType.objects.create(
            name="Sample train type name"
        )
        payload = {
            "name": "Sample train name",
            "train_type": train_type,
            "cargo_num": 10,
            "places_in_cargo": 15,
        }
        res = self.client.post(TRAIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminStationApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@test.com",
            "samplepassword43434",
            is_taff=True
        )
        self.client.force_authenticate(self.user)
        

class TrainImageUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            "admin@myproject.com", "password"
        )
        self.client.force_authenticate(self.user)
        self.train = sample_train()
        self.journey = sample_journey()

    def tearDown(self):
        self.train.image.delete()

    def test_upload_image_to_train(self):
        url = image_upload_url(self.train.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(url, {"image": ntf}, format="multipart")
        self.train.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.train.image.path))

    def test_upload_image_bad_request(self):
        url = image_upload_url(self.train.id)
        res = self.client.post(url, {"image": "not image"}, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_image_to_train_list_should_not_work(self):
        url = TRAIN_URL
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            train_type = sample_train_type()
            res = self.client.post(
                url,
                {
                    "name": "Sample train",
                    "train_type": train_type,
                    "cargo_num": 10,
                    "places_in_cargo": 60,
                    "image": ntf,
                },
                format="multipart",
            )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        train = Train.objects.get(name="Sample train")
        self.assertFalse(train.image)

    def test_image_url_is_shown_on_train_detail(self):
        url = image_upload_url(self.train.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        res = self.client.get(detail_url(self.train.id))

        self.assertIn("image", res.data)

    def test_image_url_is_shown_on_train_list(self):
        url = image_upload_url(self.train.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        res = self.client.get(TRAIN_URL)

        self.assertIn("image", res.data[0].keys())

    def test_put_train_not_allowed(self):
        train_type = TrainType.objects.create(
            name="Sample train type name"
        )
        payload = {
            "name": "Sample train name",
            "train_type": train_type,
            "cargo_num": 10,
            "places_in_cargo": 15,
        }

        train = sample_train()
        url = detail_url(train.id)

        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_train_not_allowed(self):
        train = sample_train()
        url = detail_url(train.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
