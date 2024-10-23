### Explanation of Tables

1. **Users Table**:
   - Stores user credentials and roles.
   - Uses `AUTOINCREMENT` for `user_id` to automatically generate unique IDs.

2. **Projects Table**:
   - Contains details about each project, linking the leader to the `Users` table.

3. **ProjectMembers Table**:
   - Manages the relationship between users and projects, allowing multiple users to join a project.
   - The `UNIQUE` constraint prevents duplicate user entries in the same project.

4. **Tasks Table**:
   - Holds task information, linking tasks to their respective projects and assignees.

### Functional Requirements Implementation in SQLite

- **User Authentication**:
  - Use SQL queries to insert, update, and retrieve user data from the `Users` table.
  - Implement logic to enforce role-based access during user login.

- **Task Management**:
  - Manage tasks through the `Tasks` table, where only project members can create tasks.
  - Ensure project leaders can manage members and announcements.

### SQLite Database Schema Design
```
CREATE TABLE Users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    role TEXT CHECK(role IN ('admin', 'user')) DEFAULT 'user',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Projects (
    project_id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_name TEXT NOT NULL,
    description TEXT,
    leader_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (leader_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

CREATE TABLE ProjectMembers (
    member_id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES Projects(project_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    UNIQUE(project_id, user_id)
);

CREATE TABLE Tasks (
    task_id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    due_date DATE,
    priority TEXT CHECK(priority IN ('low', 'medium', 'high')) DEFAULT 'medium',
    assignee_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES Projects(project_id) ON DELETE CASCADE,
    FOREIGN KEY (assignee_id) REFERENCES Users(user_id) ON DELETE SET NULL
);
