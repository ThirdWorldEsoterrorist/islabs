from django.db import models

class Car(models.Model):
    brand = models.CharField(max_length=100, verbose_name="Марка автомобиля")
    license_plate = models.CharField(max_length=20, unique=True, verbose_name="Государственный номер")
    year = models.IntegerField(verbose_name="Год выпуска")
    fuel_rate = models.FloatField(verbose_name="Норма расхода (л/км)")

    @property
    def total_fuel_consumption(self):
        # Вычисляем общий расход на основе всех поездок этой машины
        return sum(trip.fuel_consumption for trip in self.trip_set.all())

    def __str__(self):
        return f"{self.brand} ({self.license_plate})"

class Driver(models.Model):
    full_name = models.CharField(max_length=200, verbose_name="ФИО водителя")
    cars = models.ManyToManyField(Car, blank=True, verbose_name="Машины")

    @property
    def total_mileage(self):
        return sum(trip.distance for trip in self.trip_set.all())

    def __str__(self):
        return self.full_name

class Trip(models.Model):
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, verbose_name="Водитель")
    car = models.ForeignKey(Car, on_delete=models.CASCADE, verbose_name="Автомобиль")
    departure_time = models.DateTimeField(verbose_name="Время выезда")
    arrival_time = models.DateTimeField(verbose_name="Время заезда")
    start_mileage = models.FloatField(verbose_name="Начальный километраж")
    end_mileage = models.FloatField(verbose_name="Конечный километраж")

    @property
    def distance(self):
        # Разница между километражами
        return max(0, self.end_mileage - self.start_mileage)

    @property
    def fuel_consumption(self):
        # Пробег умноженный на норму расхода
        return self.distance * self.car.fuel_rate