# Development workflow

This is the entire workflow of this project development. Following flow chart is the entire workflow:

![join in developing - development workflow]

[join in developing - development workflow]: ../../../_images/development/contributing/join_in_developing/development.png

About the project management details, please refer to [here](https://app.clickup.com/9018752317/v/f/90183126979/90182605225).

!!! note "Different colors of flow directions"

    * General (**White**) direction: work by your hand
    * **Blue** direction: automatically work by CI

We can talk about the development workflow in different points:

## Roles

First, what thing you want to do? Think and plan what feature it should have? Exactly develop **_PyMock-Server_** by 
your hand? Or you just be interested in finding something issues for others to fix it? Different thing for different
roles:

* Developers: who's interested in developing

    The core developers could do anything for this project. Developing project code, reviewing PRs, managing the task
    tickets and estimate task states, etc. They do almost everything of this project. But the core thing is: **DESIGN**
    **SYSTEM and WRITING CODE** for this project.

    * Core developers: 
    
        Has the greatest priority to access anything of project.
    
    * Contributors or outside developers: 
    
        Only can request PR, but must wait for core developers to approve and merge it.

* Planner: who loves thinking and planning a project direction

    They would take so much time to think and consider this project direction includes what features it should support?
    What features are unnecessary and when we can deprecate and remove it? What kind of problems are the target we 
    should resolve? It has so many things should be thing, design, plan and manage of this project. Their core job is
    **DESIGNING and PLANNING** for this project.

* Tester: who's good at find issues and design tests

    They maybe not good at developing and design system. But they would be the expert to find issue and plan test. A
    feature how it should work? What thing it can do and reach to? How can test some specific features? They're good 
    at **VERIFICATION and PLAN TEST** for the project.

After clear each role's responsibility and major task they should do. Let clear their job workflow.

## Flow direction

Now we clear different roles would face different task and own different responsibility, here would tell you a task 
life cycle:

* Developers

    They would usually receive the tasks from planner or testers. About the task from planners, they would estimate 
    the task schedule and develop it.

    * Core developers: 
    
        Could develop and commit the code directly. And they also need to review PRs if it has. If reject it, please
        write detail reason or commit suggestion.
    
    * Contributors or outside developers: 
    
        After developing, only can request PR and wait for review.

* Planner

    They always think and plan the development direction and brief feature with big scope. And planner would create these 
    ideas as task ticket in **_ClickUp_**. Then developers would analyze and divide it as smaller and smaller tasks for 
    estimation and development.

* Tester

    They would create task ticket in **_ClickUp_** if they found any bugs. And they should also check whether it exists 
    the relative tests for the bug or not. If it doesn't, they should design tests for the bugs or check the PR of the 
    bug must includes test to cover the bug.

!!! note "Everyone could create task ticket!"

    In excatly, everyone could create task tickets if they need. The entire project would be 
    managed by the software service **_ClickUp_**. So the more detail of records no matter 
    who create or update, the more better to manage the project.

Above is all the development concept by roles and workflows description.
