from __future__ import annotations

from typing import Any, Dict, Optional

from ..types import JSONDict

_Sync = Any
_Async = Any


class FeaturesAPI:
    def __init__(self, transport: _Sync) -> None:
        self._transport = transport

    def compute(
        self,
        *,
        case_id: str,
        org_id: str,
        case_data: JSONDict,
        precedent_data: Optional[JSONDict] = None,
        advisory_data: Optional[JSONDict] = None,
    ) -> JSONDict:
        body: Dict[str, Any] = {
            "case_id": case_id,
            "org_id": org_id,
            "case_data": case_data,
        }
        if precedent_data is not None:
            body["precedent_data"] = precedent_data
        if advisory_data is not None:
            body["advisory_data"] = advisory_data
        return self._transport.request(
            method="POST", path="/features/compute", json_body=body
        )

    def snapshot(
        self,
        *,
        case_id: str,
        tag: Optional[str] = None,
    ) -> JSONDict:
        body: Dict[str, Any] = {"case_id": case_id}
        if tag is not None:
            body["tag"] = tag
        return self._transport.request(
            method="POST", path="/features/snapshot", json_body=body
        )

    def get_snapshot(self, snapshot_id: str) -> JSONDict:
        return self._transport.request(
            method="GET", path=f"/features/snapshot/{snapshot_id}"
        )

    def list_snapshots(
        self,
        *,
        tag: Optional[str] = None,
        case_id: Optional[str] = None,
    ) -> JSONDict:
        params: Dict[str, Any] = {}
        if tag is not None:
            params["tag"] = tag
        if case_id is not None:
            params["case_id"] = case_id
        return self._transport.request(
            method="GET", path="/features/snapshots", params=params
        )

    def explain(
        self,
        case_id: str,
        *,
        feature_key: Optional[str] = None,
    ) -> JSONDict:
        if feature_key is not None:
            return self._transport.request(
                method="GET",
                path=f"/features/explain/{case_id}/{feature_key}",
            )
        return self._transport.request(
            method="GET", path=f"/features/explain/{case_id}"
        )

    def export(self, case_id: str) -> JSONDict:
        return self._transport.request(
            method="GET", path=f"/features/export/{case_id}"
        )

    def schema(self) -> JSONDict:
        return self._transport.request(method="GET", path="/features/schema")

    def stats(self) -> JSONDict:
        return self._transport.request(method="GET", path="/features/stats")


class AsyncFeaturesAPI:
    def __init__(self, transport: _Async) -> None:
        self._transport = transport

    async def compute(
        self,
        *,
        case_id: str,
        org_id: str,
        case_data: JSONDict,
        precedent_data: Optional[JSONDict] = None,
        advisory_data: Optional[JSONDict] = None,
    ) -> JSONDict:
        body: Dict[str, Any] = {
            "case_id": case_id,
            "org_id": org_id,
            "case_data": case_data,
        }
        if precedent_data is not None:
            body["precedent_data"] = precedent_data
        if advisory_data is not None:
            body["advisory_data"] = advisory_data
        return await self._transport.request(
            method="POST", path="/features/compute", json_body=body
        )

    async def snapshot(
        self,
        *,
        case_id: str,
        tag: Optional[str] = None,
    ) -> JSONDict:
        body: Dict[str, Any] = {"case_id": case_id}
        if tag is not None:
            body["tag"] = tag
        return await self._transport.request(
            method="POST", path="/features/snapshot", json_body=body
        )

    async def get_snapshot(self, snapshot_id: str) -> JSONDict:
        return await self._transport.request(
            method="GET", path=f"/features/snapshot/{snapshot_id}"
        )

    async def list_snapshots(
        self,
        *,
        tag: Optional[str] = None,
        case_id: Optional[str] = None,
    ) -> JSONDict:
        params: Dict[str, Any] = {}
        if tag is not None:
            params["tag"] = tag
        if case_id is not None:
            params["case_id"] = case_id
        return await self._transport.request(
            method="GET", path="/features/snapshots", params=params
        )

    async def explain(
        self,
        case_id: str,
        *,
        feature_key: Optional[str] = None,
    ) -> JSONDict:
        if feature_key is not None:
            return await self._transport.request(
                method="GET",
                path=f"/features/explain/{case_id}/{feature_key}",
            )
        return await self._transport.request(
            method="GET", path=f"/features/explain/{case_id}"
        )

    async def export(self, case_id: str) -> JSONDict:
        return await self._transport.request(
            method="GET", path=f"/features/export/{case_id}"
        )

    async def schema(self) -> JSONDict:
        return await self._transport.request(
            method="GET", path="/features/schema"
        )

    async def stats(self) -> JSONDict:
        return await self._transport.request(
            method="GET", path="/features/stats"
        )
