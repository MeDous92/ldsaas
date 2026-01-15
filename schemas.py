# app/schemas.py
from typing import Optional, Any, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, constr
from enum import Enum

MAX_PWD_BYTES = 72

class UserStatus(str, Enum):
    pending = "pending"
    active = "active"
    inactive = "inactive"

class InviteIn(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    role: Optional[str] = "employee"

class InviteOut(BaseModel):
    email: EmailStr
    token: str  # raw token (only returned once to the inviter)
    name: Optional[str] = None
    invite_url: Optional[str] = None

class AcceptInviteIn(BaseModel):
    email: constr(strip_whitespace=True)
    token: str
    password: constr(min_length=8, max_length=72)

class UserOut(BaseModel):
    id: int
    email: EmailStr
    name: Optional[str] = None
    role: str
    is_active: bool
    status: UserStatus
    class Config:
        from_attributes = True

class EducationLevelOut(BaseModel):
    id: int
    name: str
    class Config:
        from_attributes = True


class CountryOut(BaseModel):
    id: int
    name: str
    code: Optional[str] = None
    class Config:
        from_attributes = True


class CityOut(BaseModel):
    id: int
    country_id: int
    name: str
    class Config:
        from_attributes = True



class UserProfileIn(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bio: Optional[str] = None
    education_level_id: Optional[int] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    postal_code: Optional[str] = None
    city_id: Optional[int] = None
    country_id: Optional[int] = None
    phone_number: Optional[str] = None
    personal_email: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    attribute1: Optional[str] = None
    attribute2: Optional[str] = None
    attribute3: Optional[str] = None
    attribute4: Optional[str] = None
    attribute5: Optional[str] = None
    attribute6: Optional[str] = None
    attribute7: Optional[str] = None
    attribute8: Optional[str] = None


class UserProfileOut(BaseModel):
    user_id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    profile_picture_url: Optional[str] = None
    bio: Optional[str] = None
    education_level_id: Optional[int] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    postal_code: Optional[str] = None
    city_id: Optional[int] = None
    country_id: Optional[int] = None
    phone_number: Optional[str] = None
    personal_email: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    attribute1: Optional[str] = None
    attribute2: Optional[str] = None
    attribute3: Optional[str] = None
    attribute4: Optional[str] = None
    attribute5: Optional[str] = None
    attribute6: Optional[str] = None
    attribute7: Optional[str] = None
    attribute8: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    class Config:
        from_attributes = True


class UserPersonalEmailOut(BaseModel):
    id: int
    user_id: int
    email: EmailStr
    is_primary: bool
    created_at: datetime
    class Config:
        from_attributes = True



class UserDependentIn(BaseModel):
    name: str
    relationship: Optional[str] = None
    date_of_birth: Optional[datetime] = None


class UserDependentOut(BaseModel):
    id: int
    user_id: int
    name: str
    relationship: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    created_at: datetime
    class Config:
        from_attributes = True

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class LoginOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserOut

class CourseOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    provider: Optional[str] = None
    provider_id: Optional[int] = None
    link: Optional[str] = None
    image: Optional[str] = None
    duration: Optional[int] = None
    duration_unit_id: Optional[int] = None
    skills: Optional[List[str]] = None
    competencies: Optional[List[str]] = None
    classification_id: Optional[int] = None
    flag_id: Optional[int] = None
    is_active: Optional[bool] = None
    assigned_by_manager: Optional[bool] = None
    assigned_by_manager_id: Optional[int] = None
    attribute1: Optional[str] = None
    attribute2: Optional[str] = None
    attribute3: Optional[str] = None
    attribute4: Optional[str] = None
    attribute5: Optional[str] = None
    attribute6: Optional[str] = None
    attribute7: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    class Config:
        from_attributes = True

class CourseEnrollmentOut(BaseModel):
    id: int
    employee_id: int
    course_id: int
    status: str
    requested_at: datetime
    approved_at: Optional[datetime] = None
    approved_by: Optional[int] = None
    deadline: Optional[datetime] = None
    course: Optional[CourseOut] = None
    class Config:
        from_attributes = True

class TeamEnrollmentOut(BaseModel):
    id: int
    status: str
    deadline: Optional[datetime] = None
    requested_at: datetime
    employee: UserOut
    course: CourseOut
    class Config:
        from_attributes = True

class NotificationOut(BaseModel):
    id: int
    user_id: int
    title: str
    body: str
    type: str
    is_read: bool
    created_at: datetime
    meta: Optional[dict[str, Any]] = Field(
        default=None,
        serialization_alias="metadata",
        validation_alias="meta",
    )
    class Config:
        from_attributes = True
