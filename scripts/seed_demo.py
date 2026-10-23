import uuid
from datetime import datetime, timezone
from sqlmodel import Session, create_engine, select, SQLModel
from app.models.base import (
    User, Workspace, WorkspaceMember, Project, Dataset, 
    DatasetColumn, ColumnProfile, CleaningRecommendation,
    Dashboard, Widget, Metric, Pipeline
)

# Corrected connection string
DATABASE_URL = "postgresql+psycopg2://user:password@deployments-db-1:5432/analytics"
engine = create_engine(DATABASE_URL)

def get_simple_hash(password: str):
    return "$2b$12$K.R8o8O.Uv1Lg.sF8kYjOe1TjFfB1B9s8S6vXfH2y8kPZkL0fE1mW"

def seed_data():
    try:
        # IMPORTANT: Create tables first because the DB is empty
        print("🛠 Creating database tables...")
        SQLModel.metadata.create_all(engine)
        
        with Session(engine) as session:
            print("🌱 Starting seeding process...")

            # 1. Create Demo User
            demo_user = User(
                email="partner@demo.ai",
                hashed_password=get_simple_hash("Partner2026!"),
                full_name="Partner Demo User",
                is_active=True
            )
            session.add(demo_user)
            session.commit()
            session.refresh(demo_user)
            print(f"✅ Created User: {demo_user.email}")

            # 2. Create Demo Workspace
            workspace = Workspace(
                name="Enterprise Global Analytics",
                slug="enterprise-global",
                settings_json='{"theme": "dark", "region": "APAC"}'
            )
            session.add(workspace)
            session.commit()
            session.refresh(workspace)
            print(f"✅ Created Workspace: {workspace.name}")

            # 3. Add User to Workspace
            member = WorkspaceMember(
                workspace_id=workspace.id,
                user_id=demo_user.id,
                role="OWNER"
            )
            session.add(member)

            # 4. Create a Demo Project
            project = Project(
                workspace_id=workspace.id,
                name="Q4 Revenue Growth Analysis",
                description="Analyzing regional revenue trends and identifying churn risks."
            )
            session.add(project)
            session.commit()
            session.refresh(project)
            print(f"✅ Created Project: {project.name}")

            # 5. Create a Demo Dataset
            dataset = Dataset(
                workspace_id=workspace.id,
                project_id=project.id,
                name="Global_Sales_2026",
                source_type="CSV",
                status="COMPLETED",
                row_count=150000
            )
            session.add(dataset)
            session.commit()
            session.refresh(dataset)

            # 6. Add Dataset Columns
            cols = [
                ("order_id", "UUID"),
                ("customer_id", "UUID"),
                ("revenue", "FLOAT"),
                ("region", "STRING"),
                ("order_date", "TIMESTAMP"),
                ("product_category", "STRING"),
            ]
            for name, dtype in cols:
                col = DatasetColumn(dataset_id=dataset.id, name=name, data_type=dtype)
                session.add(col)
                session.commit()
                session.refresh(col)
                
                profile = ColumnProfile(
                    column_id=col.id,
                    null_count=0 if "id" in name else 120,
                    distinct_count=10000 if "id" in name else 5,
                    mean_value=500.0 if name == "revenue" else None
                )
                session.add(profile)

            # 7. Add recommendations
            rec = CleaningRecommendation(
                dataset_id=dataset.id,
                rec_type="NULL_HANDLING",
                description="Found 120 nulls in 'region' column. Recommend filling with 'UNKNOWN'.",
                suggested_sql="UPDATE sales SET region = 'UNKNOWN' WHERE region IS NULL;",
                priority="HIGH"
            )
            session.add(rec)

            # 8. Demo Dashboard
            dashboard = Dashboard(
                workspace_id=workspace.id,
                name="Executive Revenue Overview",
                created_by=demo_user.id,
                layout_json='{"widgets": [{"id": "w1", "pos": [0,0]}]}'
            )
            session.add(dashboard)
            session.commit()
            session.refresh(dashboard)

            # 9. Widget
            widget = Widget(
                dashboard_id=dashboard.id,
                widget_type="TIME_SERIES_CHART",
                config_json='{"metric": "revenue", "interval": "daily"}'
            )
            session.add(widget)

            # 10. Global Metric
            metric = Metric(
                workspace_id=workspace.id,
                name="Annual Recurring Revenue (ARR)",
                formula_sql="SELECT SUM(revenue) FROM sales WHERE order_date > now() - interval '1 year'",
                aggregation_type="SUM",
                unit="USD"
            )
            session.add(metric)

            session.commit()
            print("\n🚀 SEEDING COMPLETE!")
            print(f"Demo Login: partner@demo.ai / Partner2026!")
            print(f"Workspace: {workspace.name}")
    except Exception as e:
        print(f"❌ Seeding failed: {e}")

if __name__ == "__main__":
    seed_data()
