### Database Schema Design

![DBdiagram](./doc/DBdiagram.png)         

1. **Users Table**:
   - Stores user credentials and roles.
   - Uses `AUTOINCREMENT` for `user_id` to automatically generate unique IDs.
   - Columns: 
      - `user_id`: INTEGER PRIMARY KEY
      - `username`: varchar(255) NOT NULL
      - `password`: varchar(255) NOT NULL
      - `email`: varchar(255) NOT NULL
      - `created_at`: DATETIME
  

2. **Projects Table**:
   - Contains details about each project, linking the owner_id to the `Users` table.
    - Columns: 
      - `project_id`: INTEGER PRIMARY KEY
      - `project_name`: varchar(255) NOT NULL
      - `description`: varchar(255)
      - `owner_id`: INTEGER NOT NULL (References Users)
      - `created_at`: DATETIME

3. **Tasks Table**:
   - Contains details about each tasks, linking the project_id to the `Projects` table.
   - Columns: 
      - `task_id`: INTEGER PRIMARY KEY
      - `taks_name`: varchar(255) NOT NULL
      - `description`: varchar(255)
      - `status`: enum('Not start', 'Started', 'Testing', 'Review', 'Done')
      - `priority`: enum('Low', 'Medium', 'High')
      - `due_date`: DATETIME
      - `created_at`: DATETIME

4. **UserProject Table** (Junction table for Users-Projects many-to-many relationship):
   - `user_id`: INTEGER (References Users)
   - `project_id`: INTEGER (References Projects)

5. **UserTask Table** (Junction table for Users-Tasks many-to-many relationship):
   - `user_id`: INTEGER (References Users)
   - `task_id`: INTEGER (References Tasks)

6. **ProjectTask Table** (Junction table for Projects-Tasks many-to-many relationship):
   - `project_id`: INTEGER (References Projects)
   - `task_id`: INTEGER (References Tasks)

7. **Comments Table**:
   - `user_id`: INTEGER (References Users)
   - `task_id`: INTEGER (References Tasks)
   - `comment`: varchar(255)
   - `created_at`: DATETIME


### SQLite Database Schema Design
- [SQL Schema File](./doc/schema.sql)