from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


SpecialistAgent = Literal[
    "order",
    "inventory",
    "procurement",
    "fulfillment",
    "verification",
]


class ExecutionStep(BaseModel):
    model_config = ConfigDict(extra="forbid")

    step: int = Field(ge=1)
    agent: SpecialistAgent
    action: str = Field(min_length=1, max_length=500)
    expected_output: str = Field(min_length=1, max_length=500)
    depends_on: list[int] = Field(default_factory=list)


class ExecutionPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task_type: Literal["routine", "complex"]
    problem_summary: str = Field(min_length=1, max_length=1000)
    priority: Literal["low", "medium", "high", "critical"]
    agents_required: list[SpecialistAgent] = Field(min_length=1)
    execution_plan: list[ExecutionStep] = Field(min_length=1)
    requires_human_approval: bool
    verification_required: bool

    @model_validator(mode="after")
    def validate_plan(self):
        steps = self.execution_plan
        step_numbers = [step.step for step in steps]

        if len(step_numbers) != len(set(step_numbers)):
            raise ValueError("Execution step numbers must be unique.")

        if step_numbers != sorted(step_numbers):
            raise ValueError("Execution steps must be in ascending order.")

        available_steps = set()

        for step in steps:
            if step.step in step.depends_on:
                raise ValueError(
                    f"Step {step.step} cannot depend on itself."
                )

            if len(step.depends_on) != len(set(step.depends_on)):
                raise ValueError(
                    f"Step {step.step} has duplicate dependencies."
                )

            for dependency in step.depends_on:
                if dependency not in available_steps:
                    raise ValueError(
                        f"Step {step.step} depends on invalid or "
                        f"unfinished step {dependency}."
                    )

            available_steps.add(step.step)

        step_agents = {step.agent for step in steps}
        required_agents = set(self.agents_required)

        if len(required_agents) != len(self.agents_required):
            raise ValueError("agents_required contains duplicates.")

        if step_agents != required_agents:
            raise ValueError(
                "agents_required must match the agents in execution_plan."
            )

        if self.verification_required:
            if "verification" not in required_agents:
                raise ValueError(
                    "Verification is required but no verification "
                    "step was included."
                )

        return self

