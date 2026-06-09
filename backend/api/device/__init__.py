"""Device API endpoints"""

from fastapi import APIRouter, Depends

from backend.data.equipment import Device

from .auth import get_current_device


router = APIRouter(prefix="/device", tags=["Device Endpoints"])


@router.get("/alive")
def alive():
	return {"status": "ok"}


@router.get("/current")
def get_device_info(device: Device = Depends(get_current_device)) -> Device:
	return device
