"""
LoginUser 模型（对应Java端的LoginUser类）

用于存储从Redis中解析出的登录用户信息
"""
from __future__ import annotations

from typing import Optional, Set, List, Any
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class SysRole:
    """系统角色（对应Java的SysRole）"""
    role_id: int
    role_key: str
    role_name: str
    role_sort: int
    status: str
    admin: bool = False
    data_scope: str = "1"
    dept_check_strictly: bool = False
    menu_check_strictly: bool = False
    flag: bool = False
    permissions: Set[str] = field(default_factory=set)

    @classmethod
    def from_dict(cls, data: dict) -> SysRole:
        """从字典创建实例"""
        return cls(
            role_id=int(data.get("roleId", 0)),
            role_key=data.get("roleKey", ""),
            role_name=data.get("roleName", ""),
            role_sort=int(data.get("roleSort", 0)),
            status=data.get("status", "0"),
            admin=data.get("admin", False),
            data_scope=data.get("dataScope", "1"),
            dept_check_strictly=data.get("deptCheckStrictly", False),
            menu_check_strictly=data.get("menuCheckStrictly", False),
            flag=data.get("flag", False),
            permissions=set(data.get("permissions", [])) if data.get("permissions") else set(),
        )


@dataclass
class SysUser:
    """系统用户（对应Java的SysUser）"""
    user_id: int
    user_name: str
    nick_name: str
    status: str
    del_flag: str
    admin: bool = False
    phonenumber: Optional[str] = None
    sex: Optional[str] = None
    create_by: Optional[str] = None
    create_time: Optional[str] = None
    pwd_update_date: Optional[str] = None
    login_date: Optional[str] = None
    login_ip: Optional[str] = None
    roles: List[SysRole] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> SysUser:
        """从字典创建实例"""
        roles = []
        if data.get("roles"):
            roles = [SysRole.from_dict(role) for role in data["roles"]]

        return cls(
            user_id=int(data.get("userId", 0)),
            user_name=data.get("userName", ""),
            nick_name=data.get("nickName", ""),
            status=data.get("status", "0"),
            del_flag=data.get("delFlag", "0"),
            admin=data.get("admin", False),
            phonenumber=data.get("phonenumber"),
            sex=data.get("sex"),
            create_by=data.get("createBy"),
            create_time=data.get("createTime"),
            pwd_update_date=data.get("pwdUpdateDate"),
            login_date=data.get("loginDate"),
            login_ip=data.get("loginIp"),
            roles=roles,
        )


@dataclass
class LoginUser:
    """
    登录用户身份权限（对应Java的LoginUser类）

    从Redis中解析的用户信息，用于Token验证
    """


    user_id: int
    dept_id: Optional[int] = None
    token: Optional[str] = None
    login_time: Optional[int] = None
    expire_time: Optional[int] = None
    ipaddr: Optional[str] = None
    login_location: Optional[str] = None
    browser: Optional[str] = None
    os: Optional[str] = None
    permissions: Set[str] = field(default_factory=set)
    user: Optional[SysUser] = None
    username: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> LoginUser:
        """从字典创建实例"""
        user = None
        if data.get("user"):
            user = SysUser.from_dict(data["user"])

        permissions: set[str] = set(data.get("permissions", [])) if data.get("permissions") else set()
        if user and user.roles:
            for role in user.roles:
                permissions.update(role.permissions)
                if role.admin:
                    permissions.add("*:*:*")

        return cls(
            user_id=int(data.get("userId", 0)),
            dept_id=int(data["deptId"]) if data.get("deptId") else None,
            token=data.get("token"),
            login_time=int(data["loginTime"]) if data.get("loginTime") else None,
            expire_time=int(data["expireTime"]) if data.get("expireTime") else None,
            ipaddr=data.get("ipaddr"),
            login_location=data.get("loginLocation"),
            browser=data.get("browser"),
            os=data.get("os"),
            permissions=permissions,
            user=user,
            username=data.get("username") or (user.user_name if user else None),
        )

    def is_expired(self) -> bool:
        """检查Token是否过期"""
        if not self.expire_time:
            return False
        expire_seconds = self.expire_time / 1000
        return datetime.now().timestamp() > expire_seconds

    def has_permission(self, permission: str) -> bool:
        """检查是否有指定权限"""
        return permission in self.permissions

    def has_any_permission(self, permissions: list[str]) -> bool:
        """检查是否有任一权限"""
        return any(p in self.permissions for p in permissions)

    def has_all_permissions(self, permissions: list[str]) -> bool:
        """检查是否有所有权限"""
        return all(p in self.permissions for p in permissions)

    def get_scopes(self) -> list[str]:
        """
        将permissions转换为FastAPI风格的scopes
        例如：tool:manage:create -> tools:write
        """
        scope_mapping = {
            "create": "write",
            "update": "write",
            "delete": "write",
            "list": "read",
            "view": "read",
            "enable": "write",
            "config": "write",
        }

        scopes = set()
        if self.user and any(role.admin for role in self.user.roles):
            scopes.add("admin")

        for perm in self.permissions:
            parts = perm.split(":")
            if len(parts) >= 3:
                resource = parts[0]
                action = parts[-1]

                if action in scope_mapping:
                    scope = f"{resource}s:{scope_mapping[action]}"
                    scopes.add(scope)

        if "admin" in scopes or "*:*:*" in self.permissions:
            scopes.add("*")

        return list(scopes)
