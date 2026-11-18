import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi import HTTPException, Request, Response

from src.app import (
    LoginRequest,
    SESSION_COOKIE_NAME,
    activities,
    create_session_token,
    get_session_username,
    hash_password,
    login,
    require_teacher,
    signup_for_activity,
    unregister_from_activity,
    verify_password,
)


def make_request(cookie: str | None = None) -> Request:
    headers = []
    if cookie is not None:
        headers.append((b"cookie", cookie.encode("ascii")))
    return Request({"type": "http", "headers": headers})


class TeacherAuthenticationTests(unittest.TestCase):
    def test_password_hash_verifies_only_the_original_password(self):
        password_hash = hash_password("correct horse battery staple")

        self.assertTrue(verify_password("correct horse battery staple", password_hash))
        self.assertFalse(verify_password("wrong password", password_hash))
        self.assertFalse(verify_password("wrong format", "not-a-password-hash"))

    def test_session_token_identifies_teacher_and_rejects_tampering(self):
        token = create_session_token("teacher")

        self.assertEqual(
            get_session_username(make_request(f"{SESSION_COOKIE_NAME}={token}")),
            "teacher",
        )
        self.assertIsNone(
            get_session_username(make_request(f"{SESSION_COOKIE_NAME}={token}x"))
        )

    def test_login_accepts_configured_teacher_and_rejects_wrong_password(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            credentials_file = Path(temporary_directory) / "teachers.json"
            credentials_file.write_text(
                json.dumps(
                    {"teachers": {"teacher": hash_password("teacher-password")}}
                ),
                encoding="utf-8",
            )
            with patch("src.app.TEACHER_CREDENTIALS_FILE", credentials_file):
                response = Response()
                result = login(
                    LoginRequest(username="teacher", password="teacher-password"),
                    response,
                )
                cookie = response.headers["set-cookie"].split(";", 1)[0]

                self.assertEqual(result["username"], "teacher")
                self.assertEqual(
                    require_teacher(make_request(cookie)),
                    "teacher",
                )
                with self.assertRaises(HTTPException) as login_error:
                    login(
                        LoginRequest(username="teacher", password="wrong-password"),
                        Response(),
                    )
                self.assertEqual(login_error.exception.status_code, 401)

    def test_students_cannot_register_or_unregister(self):
        activity_name = "Chess Club"
        original_participants = activities[activity_name]["participants"].copy()
        request = make_request()

        with self.assertRaises(HTTPException) as signup_error:
            signup_for_activity(activity_name, "new-student@mergington.edu", request)
        self.assertEqual(signup_error.exception.status_code, 401)

        with self.assertRaises(HTTPException) as unregister_error:
            unregister_from_activity(
                activity_name, original_participants[0], request
            )
        self.assertEqual(unregister_error.exception.status_code, 401)
        self.assertEqual(activities[activity_name]["participants"], original_participants)


if __name__ == "__main__":
    unittest.main()
