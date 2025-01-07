# Alembic Migration for SQLite

This guide explains how to use Alembic to alter tables in SQLite, as SQLite doesn't support some direct table modifications like other SQL databases.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Handling SQLite Limitations](#handling-sqlite-limitations)
- [Contributing](#contributing)
- [License](#license)

## Prerequisites
- Python 3.7 or later
- Alembic installed via pip
- SQLite database

## Installation
1. Install Alembic:
    ```bash
    pip install alembic
    ```

2. Initialize Alembic in your project directory:
    ```bash
    alembic init alembic
    ```

3. Modify the `alembic.ini` file to point to your SQLite database:
    ```ini
    sqlalchemy.url = sqlite:///yourdatabase.db
    ```

## Usage
1. Create a new migration script:
    ```bash
    alembic revision --autogenerate -m "Add new columns to product table"
    ```

2. Modify the generated migration script (located in the `alembic/versions` folder) to add new columns:
    ```python
    from alembic import op
    import sqlalchemy as sa

    # Revision identifiers, used by Alembic.
    revision = 'your_revision_id'
    down_revision = 'previous_revision_id'
    branch_labels = None
    depends_on = None

    def upgrade():
        # Add new columns to 'product' table
        op.add_column('product', sa.Column('image_filename', sa.String(length=255), nullable=True))
        op.add_column('product', sa.Column('description', sa.String(length=255), nullable=True))

    def downgrade():
        # Remove columns from 'product' table
        op.drop_column('product', 'image_filename')
        op.drop_column('product', 'description')
    ```

3. Apply the migration and update your SQLite database:
    ```bash
    alembic upgrade head
    ```

## Handling SQLite Limitations
SQLite does not support some direct table modifications like adding or dropping columns. Alembic provides a workaround by creating a new table with the desired schema, copying the data, and then renaming the new table.

### Example: Adding a Column
To add a column to an SQLite table, you can follow this approach:

1. Create a new migration script:
    ```bash
    alembic revision -m "Add new column to product table"
    ```

2. Modify the migration script to handle SQLite limitations:
    ```python
    from alembic import op
    import sqlalchemy as sa
    from sqlalchemy.sql import table, column

    # Revision identifiers, used by Alembic.
    revision = 'your_revision_id'
    down_revision = 'previous_revision_id'
    branch_labels = None
    depends_on = None

    def upgrade():
        # Create a new table with the additional column
        op.create_table(
            'product_new',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('name', sa.String(length=255), nullable=False),
            sa.Column('image_filename', sa.String(length=255), nullable=True),
            sa.Column('description', sa.String(length=255), nullable=True)
        )

        # Copy data from the old table to the new table
        product_old = table('product', 
            column('id', sa.Integer),
            column('name', sa.String)
        )
        product_new = table('product_new', 
            column('id', sa.Integer),
            column('name', sa.String),
            column('image_filename', sa.String),
            column('description', sa.String)
        )
        op.execute(product_new.insert().from_select(
            ['id', 'name'],
            op.select([product_old.c.id, product_old.c.name])
        ))

        # Drop the old table
        op.drop_table('product')

        # Rename the new table to the old table's name
        op.rename_table('product_new', 'product')

    def downgrade():
        # Create the old table without the additional column
        op.create_table(
            'product_old',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('name', sa.String(length=255), nullable=False)
        )

        # Copy data from the new table to the old table
        product_new = table('product', 
            column('id', sa.Integer),
            column('name', sa.String)
        )
        product_old = table('product_old', 
            column('id', sa.Integer),
            column('name', sa.String)
        )
        op.execute(product_old.insert().from_select(
            ['id', 'name'],
            op.select([product_new.c.id, product_new.c.name])
        ))

        # Drop the new table
        op.drop_table('product')

        # Rename the old table to the new table's name
        op.rename_table('product_old', 'product')
    ```

## Contributing
If you would like to contribute to this project, please follow the guidelines outlined in the [CONTRIBUTING.md](CONTRIBUTING.md) file.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
