"""
Training Service for managing training plans and nominations.
"""

import uuid
from datetime import datetime
from typing import Optional

from src.training_models import (
    Employee, TrainingPlan, AreaOfWork, Nomination,
    NominationStatus, TrainingPriority, TrainingStatus
)
from src.notification_service import NotificationService


class TrainingService:
    """Service for managing training plans and employee nominations."""

    def __init__(self, notification_config: Optional[dict] = None):
        """Initialize training service."""
        self.notification_service = NotificationService(notification_config)

        # In-memory storage (in production, use database)
        self.employees: dict[str, Employee] = {}
        self.training_plans: dict[str, TrainingPlan] = {}
        self.nominations: dict[str, Nomination] = {}

        # Initialize with sample data
        self._initialize_sample_data()

    def _initialize_sample_data(self):
        """Initialize with sample employees and training plans."""

        # Sample employees
        sample_employees = [
            Employee(
                id="emp001",
                name="John Smith",
                email="john.smith@company.com",
                department="Engineering",
                role="Software Developer"
            ),
            Employee(
                id="emp002",
                name="Sarah Johnson",
                email="sarah.johnson@company.com",
                department="Engineering",
                role="Senior Developer"
            ),
            Employee(
                id="emp003",
                name="Michael Chen",
                email="michael.chen@company.com",
                department="QA",
                role="QA Engineer"
            ),
            Employee(
                id="emp004",
                name="Emily Davis",
                email="emily.davis@company.com",
                department="DevOps",
                role="DevOps Engineer"
            ),
            Employee(
                id="emp005",
                name="Robert Wilson",
                email="robert.wilson@company.com",
                department="Engineering",
                role="Tech Lead"
            ),
            Employee(
                id="emp006",
                name="Jennifer Martinez",
                email="jennifer.martinez@company.com",
                department="Product",
                role="Product Manager"
            ),
            Employee(
                id="emp007",
                name="David Thompson",
                email="david.thompson@company.com",
                department="Engineering",
                role="Junior Developer"
            ),
            Employee(
                id="emp008",
                name="Lisa Anderson",
                email="lisa.anderson@company.com",
                department="Design",
                role="UX Designer"
            ),
            # Technical SPOCs for reviewing
            Employee(
                id="spoc001",
                name="Alex Kumar",
                email="alex.kumar@company.com",
                department="Engineering",
                role="Technical SPOC"
            ),
            Employee(
                id="spoc002",
                name="Maria Garcia",
                email="maria.garcia@company.com",
                department="Engineering",
                role="Technical SPOC"
            ),
            Employee(
                id="spoc003",
                name="James Park",
                email="james.park@company.com",
                department="Architecture",
                role="Technical SPOC"
            ),
        ]

        for emp in sample_employees:
            self.employees[emp.id] = emp

        # Sample training plans with AOWs
        sample_plans = [
            TrainingPlan(
                id="tp001",
                name="Python Development Fundamentals",
                description="Comprehensive training on Python development best practices",
                created_by="HR Admin",
                areas_of_work=[
                    AreaOfWork(
                        id="aow001",
                        name="Python Basics",
                        description="Core Python syntax, data types, and control structures",
                        skills=["Python syntax", "Data types", "Control flow", "Functions"],
                        duration_hours=16,
                        resources=["Python Documentation", "Practice Exercises"],
                        prerequisites=[]
                    ),
                    AreaOfWork(
                        id="aow002",
                        name="Object-Oriented Programming",
                        description="Classes, inheritance, and design patterns in Python",
                        skills=["Classes", "Inheritance", "Polymorphism", "Design Patterns"],
                        duration_hours=20,
                        resources=["OOP Guide", "Design Patterns Book"],
                        prerequisites=["Python Basics"]
                    ),
                    AreaOfWork(
                        id="aow003",
                        name="Testing with Pytest",
                        description="Unit testing, mocking, and test automation",
                        skills=["Unit Testing", "Pytest", "Mocking", "TDD"],
                        duration_hours=12,
                        resources=["Pytest Documentation", "TDD Workshop"],
                        prerequisites=["Python Basics", "Object-Oriented Programming"]
                    ),
                ]
            ),
            TrainingPlan(
                id="tp002",
                name="DevOps & CI/CD Pipeline",
                description="Learn to build and maintain CI/CD pipelines",
                created_by="HR Admin",
                areas_of_work=[
                    AreaOfWork(
                        id="aow004",
                        name="Version Control with Git",
                        description="Git workflows, branching strategies, and collaboration",
                        skills=["Git", "Branching", "Merging", "Collaboration"],
                        duration_hours=8,
                        resources=["Git Pro Book", "Interactive Tutorial"],
                        prerequisites=[]
                    ),
                    AreaOfWork(
                        id="aow005",
                        name="Docker Containerization",
                        description="Container basics, Dockerfile creation, and orchestration",
                        skills=["Docker", "Containers", "Dockerfile", "Docker Compose"],
                        duration_hours=16,
                        resources=["Docker Documentation", "Hands-on Labs"],
                        prerequisites=["Version Control with Git"]
                    ),
                    AreaOfWork(
                        id="aow006",
                        name="CI/CD with GitHub Actions",
                        description="Automated testing, building, and deployment pipelines",
                        skills=["GitHub Actions", "CI/CD", "Automation", "Deployment"],
                        duration_hours=12,
                        resources=["GitHub Actions Docs", "Pipeline Templates"],
                        prerequisites=["Version Control with Git", "Docker Containerization"]
                    ),
                ]
            ),
            TrainingPlan(
                id="tp003",
                name="Cloud Architecture Essentials",
                description="Fundamentals of cloud computing and architecture",
                created_by="HR Admin",
                areas_of_work=[
                    AreaOfWork(
                        id="aow007",
                        name="Cloud Computing Fundamentals",
                        description="Core concepts of cloud computing and service models",
                        skills=["IaaS", "PaaS", "SaaS", "Cloud Concepts"],
                        duration_hours=8,
                        resources=["Cloud Computing Guide", "AWS/Azure Basics"],
                        prerequisites=[]
                    ),
                    AreaOfWork(
                        id="aow008",
                        name="Infrastructure as Code",
                        description="Managing infrastructure with Terraform and CloudFormation",
                        skills=["Terraform", "CloudFormation", "IaC", "Automation"],
                        duration_hours=20,
                        resources=["Terraform Docs", "IaC Best Practices"],
                        prerequisites=["Cloud Computing Fundamentals"]
                    ),
                    AreaOfWork(
                        id="aow009",
                        name="Kubernetes Orchestration",
                        description="Container orchestration with Kubernetes",
                        skills=["Kubernetes", "Pods", "Services", "Deployments"],
                        duration_hours=24,
                        resources=["Kubernetes Docs", "K8s Labs"],
                        prerequisites=["Cloud Computing Fundamentals", "Docker Containerization"]
                    ),
                ]
            ),
        ]

        for plan in sample_plans:
            self.training_plans[plan.id] = plan

    # Employee Management
    def get_all_employees(self) -> list[Employee]:
        """Get all employees."""
        return list(self.employees.values())

    def get_employee(self, employee_id: str) -> Optional[Employee]:
        """Get employee by ID."""
        return self.employees.get(employee_id)

    def get_employees_by_department(self, department: str) -> list[Employee]:
        """Get employees by department."""
        return [e for e in self.employees.values() if e.department == department]

    # Training Plan Management
    def get_all_training_plans(self) -> list[TrainingPlan]:
        """Get all training plans."""
        return list(self.training_plans.values())

    def get_training_plan(self, plan_id: str) -> Optional[TrainingPlan]:
        """Get training plan by ID."""
        return self.training_plans.get(plan_id)

    def get_aow(self, plan_id: str, aow_id: str) -> Optional[AreaOfWork]:
        """Get specific area of work."""
        plan = self.training_plans.get(plan_id)
        if plan:
            for aow in plan.areas_of_work:
                if aow.id == aow_id:
                    return aow
        return None

    # Nomination Workflow
    def nominate_employee(
        self,
        training_plan_id: str,
        aow_id: str,
        employee_id: str,
        nominated_by: str,
        priority: str = "medium",
        notes: str = ""
    ) -> dict:
        """
        Nominate an employee for training and send notification.

        This is the main workflow method that:
        1. Validates the nomination
        2. Creates the nomination record
        3. Sends email notification
        4. Returns the result
        """

        # Validate training plan
        training_plan = self.training_plans.get(training_plan_id)
        if not training_plan:
            return {
                'success': False,
                'error': f'Training plan not found: {training_plan_id}'
            }

        # Validate AOW
        aow = self.get_aow(training_plan_id, aow_id)
        if not aow:
            return {
                'success': False,
                'error': f'Area of Work not found: {aow_id}'
            }

        # Validate employee
        employee = self.employees.get(employee_id)
        if not employee:
            return {
                'success': False,
                'error': f'Employee not found: {employee_id}'
            }

        # Check for existing nomination
        existing = self._get_existing_nomination(training_plan_id, aow_id, employee_id)
        if existing and existing.status not in [NominationStatus.DECLINED, NominationStatus.COMPLETED]:
            return {
                'success': False,
                'error': f'Employee {employee.name} already has an active nomination for this training'
            }

        # Create nomination
        priority_enum = TrainingPriority(priority.lower())
        nomination = Nomination(
            id=str(uuid.uuid4()),
            training_plan_id=training_plan_id,
            aow_id=aow_id,
            employee_id=employee_id,
            nominated_by=nominated_by,
            priority=priority_enum,
            notes=notes,
            training_status=TrainingStatus.INITIATED,
            initiated_at=datetime.now()
        )

        # Send notification
        success, notification = self.notification_service.send_nomination_notification(
            employee=employee,
            training_plan=training_plan,
            aow=aow,
            nomination=nomination,
            nominated_by_name=nominated_by
        )

        if success:
            nomination.status = NominationStatus.NOTIFIED
            nomination.notified_at = datetime.now()
        else:
            nomination.status = NominationStatus.PENDING

        # Store nomination
        self.nominations[nomination.id] = nomination

        return {
            'success': True,
            'nomination': nomination.to_dict(),
            'notification': notification.to_dict(),
            'message': f'Successfully nominated {employee.name} for {aow.name}' +
                      (' and sent email notification' if success else ' (email notification pending)')
        }

    def _get_existing_nomination(
        self,
        training_plan_id: str,
        aow_id: str,
        employee_id: str
    ) -> Optional[Nomination]:
        """Check if nomination already exists."""
        for nomination in self.nominations.values():
            if (nomination.training_plan_id == training_plan_id and
                nomination.aow_id == aow_id and
                nomination.employee_id == employee_id):
                return nomination
        return None

    def get_nominations_for_employee(self, employee_id: str) -> list[Nomination]:
        """Get all nominations for an employee."""
        return [n for n in self.nominations.values() if n.employee_id == employee_id]

    def get_nominations_for_plan(self, plan_id: str) -> list[Nomination]:
        """Get all nominations for a training plan."""
        return [n for n in self.nominations.values() if n.training_plan_id == plan_id]

    def get_nominations_for_aow(self, plan_id: str, aow_id: str) -> list[Nomination]:
        """Get all nominations for a specific AOW."""
        return [
            n for n in self.nominations.values()
            if n.training_plan_id == plan_id and n.aow_id == aow_id
        ]

    def get_all_nominations(self) -> list[Nomination]:
        """Get all nominations."""
        return list(self.nominations.values())

    def update_nomination_status(
        self,
        nomination_id: str,
        status: str
    ) -> dict:
        """Update nomination status."""
        nomination = self.nominations.get(nomination_id)
        if not nomination:
            return {
                'success': False,
                'error': f'Nomination not found: {nomination_id}'
            }

        nomination.status = NominationStatus(status)
        if status == 'completed':
            nomination.completed_at = datetime.now()

        return {
            'success': True,
            'nomination': nomination.to_dict(),
            'message': f'Nomination status updated to {status}'
        }

    # Technical SPOC Management
    def get_technical_spocs(self) -> list[Employee]:
        """Get all Technical SPOCs for reviewer dropdown."""
        return [e for e in self.employees.values() if e.role == "Technical SPOC"]

    def assign_reviewer(
        self,
        nomination_id: str,
        reviewer_id: str
    ) -> dict:
        """Assign a Technical SPOC as reviewer for a nomination."""
        nomination = self.nominations.get(nomination_id)
        if not nomination:
            return {
                'success': False,
                'error': f'Nomination not found: {nomination_id}'
            }

        reviewer = self.employees.get(reviewer_id)
        if not reviewer:
            return {
                'success': False,
                'error': f'Reviewer not found: {reviewer_id}'
            }

        nomination.reviewed_by = reviewer_id
        nomination.reviewed_at = datetime.now()

        return {
            'success': True,
            'nomination': nomination.to_dict(),
            'message': f'Reviewer {reviewer.name} assigned successfully'
        }

    def update_training_status(
        self,
        nomination_id: str,
        training_status: str
    ) -> dict:
        """Update training status for a nomination."""
        nomination = self.nominations.get(nomination_id)
        if not nomination:
            return {
                'success': False,
                'error': f'Nomination not found: {nomination_id}'
            }

        try:
            status_enum = TrainingStatus(training_status.lower())
        except ValueError:
            return {
                'success': False,
                'error': f'Invalid training status: {training_status}'
            }

        nomination.training_status = status_enum

        # Update corresponding date
        if training_status == 'initiated':
            nomination.initiated_at = datetime.now()
        elif training_status == 'in_progress':
            nomination.in_progress_at = datetime.now()
        elif training_status == 'completed':
            nomination.completed_at = datetime.now()

        return {
            'success': True,
            'nomination': nomination.to_dict(),
            'message': f'Training status updated to {training_status}'
        }

    # Dashboard/Summary Methods
    def get_training_summary(self) -> dict:
        """Get summary of training nominations."""
        total_nominations = len(self.nominations)
        status_counts = {}
        training_status_counts = {}

        for nomination in self.nominations.values():
            status = nomination.status.value
            status_counts[status] = status_counts.get(status, 0) + 1

            t_status = nomination.training_status.value
            training_status_counts[t_status] = training_status_counts.get(t_status, 0) + 1

        return {
            'total_employees': len(self.employees),
            'total_training_plans': len(self.training_plans),
            'total_nominations': total_nominations,
            'nominations_by_status': status_counts,
            'nominations_by_training_status': training_status_counts
        }
