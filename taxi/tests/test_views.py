from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from taxi.models import Driver, Car, Manufacturer

DRIVER_URL = reverse("taxi:driver-list")
# User
TEST_USER_USERNAME = "testuser"
TEST_USER_PASSWORD = "testPass123"
TEST_USER_LICENSE = "TST12345"
TEST_USER_FIRST_NAME = "<NAME1>"
TEST_USER_LAST_NAME = "<SURNAME1>"

# Manufacturer
TEST_MANUFACTURER_NAME = "Test Motors"
TEST_MANUFACTURER_COUNTRY = "Test Country"

# Car
TEST_CAR_MODEL = "Audi A3"
TEST_CAR_LICENSE_PLATE = "AA1234BB"


class PublicDriverTests(TestCase):
    def test_login_required(self):
        res = self.client.get(DRIVER_URL)
        self.assertEqual(res.status_code, 302)
        self.assertIn("/accounts/login/", res.url)


class PrivateDriverTests(TestCase):
    def setUp(self):
        self.user1 = get_user_model().objects.create_user(
            username="u1",
            password="pass",
            license_number="TST12345",
            first_name="<NAME>",
            last_name="<SURNAME>",
        )
        self.user2 = get_user_model().objects.create_user(
            username="u2",
            password="pass",
            license_number="TST54321",
            first_name="<NAME1>",
            last_name="<SURNAME1>",
        )
        self.client.force_login(self.user1)

    def test_retreat_drivers(self):
        response = self.client.get(DRIVER_URL)
        self.assertEqual(response.status_code, 200)
        drivers = get_user_model().objects.all()
        self.assertEqual(len(drivers), 2)
        self.assertEqual(
            list(response.context["driver_list"]),
            list(drivers),
        )
        self.assertTemplateUsed(response, "taxi/driver_list.html")


class PrivateCarViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = get_user_model()
        cls.user = user.objects.create_user(
            username=TEST_USER_USERNAME,
            password=TEST_USER_PASSWORD,
            license_number=TEST_USER_LICENSE,
            first_name=TEST_USER_FIRST_NAME,
            last_name=TEST_USER_LAST_NAME,
        )
        cls.manufacturer = Manufacturer.objects.create(
            name=TEST_MANUFACTURER_NAME, country=TEST_MANUFACTURER_COUNTRY
        )
        cls.driver = user.objects.get(username=cls.user.username)
        cls.car = Car.objects.create(
            model=TEST_CAR_MODEL, manufacturer=cls.manufacturer
        )
        cls.car.drivers.add(cls.driver)

    def setUp(self):
        self.client.force_login(self.user)

    def test_car_update_view(self):
        url = reverse("taxi:car-update", args=[self.car.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "taxi/car_form.html")
        self.assertContains(response, self.car.model)

    def test_car_update_view_post(self):
        url = reverse("taxi:car-update", args=[self.car.id])
        data = {
            "model": "Audi A4",
            "drivers": [self.driver.id],
            "manufacturer": self.manufacturer.id,
        }
        response = self.client.post(url, data)
        self.car.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.car.model, data.get("model"))

    # ---- DeleteView ----
    def test_car_delete_view_get(self):
        url = reverse("taxi:car-delete", args=[self.car.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "taxi/car_confirm_delete.html")
        self.assertContains(response, self.car.model)

    def test_car_delete_view_post(self):
        url = reverse("taxi:car-delete", args=[self.car.id])
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("taxi:car-list"))
        self.assertFalse(Car.objects.filter(id=self.car.id).exists())


class PrivateManufacturerViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = get_user_model()
        cls.user = user.objects.create_user(
            username=TEST_USER_USERNAME,
            password=TEST_USER_PASSWORD,
            license_number=TEST_USER_LICENSE,
            first_name=TEST_USER_FIRST_NAME,
            last_name=TEST_USER_LAST_NAME,
        )
        cls.manufacturer = Manufacturer.objects.create(
            name=TEST_MANUFACTURER_NAME, country=TEST_MANUFACTURER_COUNTRY
        )

    def setUp(self):
        self.client.force_login(self.user)

    def test_manufacturer_update_view(self):
        url = reverse("taxi:manufacturer-update", args=[self.manufacturer.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "taxi/manufacturer_form.html")
        self.assertContains(response, self.manufacturer.name)

    def test_manufacturer_update_view_post(self):
        url = reverse("taxi:manufacturer-update", args=[self.manufacturer.id])
        data = {
            "name": "test_name2",
            "country": self.manufacturer.country,
        }
        response = self.client.post(url, data)
        self.manufacturer.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.manufacturer.name, data.get("name"))

    # ---- DeleteView ----
    def test_manufacturer_delete_view_get(self):
        url = reverse("taxi:manufacturer-delete", args=[self.manufacturer.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "taxi/manufacturer_confirm_delete.html"
        )
        self.assertContains(response, self.manufacturer.name)

    def test_manufacturer_delete_view_post(self):
        url = reverse("taxi:manufacturer-delete", args=[self.manufacturer.id])
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("taxi:manufacturer-list"))
        self.assertFalse(
            Manufacturer.objects.filter(id=self.manufacturer.id).exists()
        )
