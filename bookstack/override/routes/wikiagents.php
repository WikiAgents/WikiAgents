<?php

/**
 * Routes for the BookStack API.
 * Routes have a uri prefix of /wikiagents/.
 * Controllers all end with "ApiController"
 */

use Illuminate\Support\Facades\Route;
use BookStack\WikiAgents\TestApiController;
use BookStack\WikiAgents\CommentAPIController;
use BookStack\WikiAgents\BookToShelfAPIController;
use BookStack\WikiAgents\AttachmentExtensionAPIController;

Route::get('wtf', [TestApiController::class, 'get']);

Route::get('book_project_membership/{id}', [BookToShelfAPIController::class, 'get'])->middleware('api');


// Route::get('/api/comments', [CommentApiController::class, 'list'])
//     ->middleware('api');

// Route::get('comments', [CommentAPIController::class, 'list']) ->middleware('api');
Route::post('/comments', [CommentAPIController::class, 'create']) ->middleware('api');


