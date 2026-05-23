import json
from django.shortcuts import render
from django.http import JsonResponse
from .models import *

def index(request):
    return render(request, 'index.html')

def cars_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            fuel_rate = float(data.get('fuel_rate', 0))
            license_plate = data.get('license_plate')

            # Проверки по ТЗ
            if fuel_rate <= 0:
                return JsonResponse({'success': False, 'error': 'Норма расхода должна быть больше 0.'})
            if Car.objects.filter(license_plate=license_plate).exists():
                return JsonResponse({'success': False, 'error': 'Государственный номер уже существует.'})

            Car.objects.create(
                brand=data.get('brand'),
                license_plate=license_plate,
                year=int(data.get('year')),
                fuel_rate=fuel_rate
            )
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    cars = Car.objects.all()
    return render(request, 'cars.html', {'cars': cars})

def drivers_view(request):
    drivers = Driver.objects.all()
    return render(request, 'drivers.html', {'drivers': drivers})

def trips_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            driver_id = data.get('driver_id')
            car_id = data.get('car_id')

            # 1. Находим водителя в базе данных
            try:
                driver = Driver.objects.get(id=driver_id)
            except Driver.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Указанный водитель не найден.'})

            # 2. Проверяем, привязана ли выбранная машина к этому водителю
            if not driver.cars.filter(id=car_id).exists():
                return JsonResponse({
                    'success': False,
                    'error': 'Ошибка: выбранный автомобиль не принадлежит этому водителю!'
                })

            # 3. Если проверка прошла успешно, сохраняем поездку
            Trip.objects.create(
                driver_id=driver_id,
                car_id=car_id,
                departure_time=data.get('departure_time'),
                arrival_time=data.get('arrival_time'),
                start_mileage=float(data.get('start_mileage')),
                end_mileage=float(data.get('end_mileage'))
            )
            return JsonResponse({'success': True})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    trips = Trip.objects.all()
    return render(request, 'trips.html', {
        'trips': trips,
        'drivers': Driver.objects.all(),
        'cars': Car.objects.all()
    })