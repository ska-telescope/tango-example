from logging import Logger
from typing import Any, Callable

from ska_control_model import TaskStatus
from ska_tango_base.base.component_manager import (
    BaseComponentManager,
    CommunicationStatusCallbackType,
    TaskCallbackType,
)


class GenericComponentManager(BaseComponentManager):
    def __init__(
        self: BaseComponentManager,
        logger: Logger,
        communication_state_callback: CommunicationStatusCallbackType
        | None = None,
        component_state_callback: Callable[..., None] | None = None,
        **state: Any
    ) -> None:
        super().__init__(
            logger,
            communication_state_callback,
            component_state_callback,
            **state
        )

    def abort_commands(
        self: BaseComponentManager,
        task_callback: TaskCallbackType | None = None,
    ) -> tuple[TaskStatus, str]:
        return

    def off(
        self: BaseComponentManager,
        task_callback: TaskCallbackType | None = None,
    ) -> tuple[TaskStatus, str]:
        return

    def on(
        self: BaseComponentManager,
        task_callback: TaskCallbackType | None = None,
    ) -> tuple[TaskStatus, str]:
        return

    def reset(
        self: BaseComponentManager,
        task_callback: TaskCallbackType | None = None,
    ) -> tuple[TaskStatus, str]:
        return

    def standby(
        self: BaseComponentManager,
        task_callback: TaskCallbackType | None = None,
    ) -> tuple[TaskStatus, str]:
        return

    def start_communicating(self: BaseComponentManager) -> None:
        return

    def stop_communicating(self: BaseComponentManager) -> None:
        return
