<?php

namespace Database\Seeders;

use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;
use App\Models\Task;

class TaskSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        Task::create([
            'title' => "Моя задача",
            'description' =>  "Описание задачи",
            'status' => 'pending'
        ]);

        Task::create([
            "title"=> "задача 2",
            "description"=> "Начать изучение php",
            "status"=> "completed"
        ]);

        Task::create([
            "title"=> "задача 3",
            "description"=> "Начать изучение laravel",
            "status"=> "completed"
        ]);
        Task::create([
            "title"=> "задача 3.5",
            "description"=> "Протестировать PATCH в postman из-за опечатки.",
            "status"=> "completed"
        ]);
        Task::create([
        "title"=> "задача 4",
        "description"=> "Добавить решение тестового задания в репозиторий githab.",
        "status"=> "completed"
        ]);
    }
}
