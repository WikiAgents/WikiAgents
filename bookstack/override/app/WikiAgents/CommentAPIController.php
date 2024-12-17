<?php

namespace BookStack\WikiAgents;


use BookStack\Activity\Models\Comment;
use BookStack\Http\ApiController;
use BookStack\Activity\CommentRepo;
use BookStack\Entities\Queries\PageQueries;
use Illuminate\Http\Request;


class CommentAPIController extends ApiController
{
    public function __construct(
        protected CommentRepo $commentRepo,
        protected PageQueries $pageQueries,
    ) {
    }

    public function list()
    {
        return $this->apiListingResponse(Comment::query()->with('createdBy'), [
            'id', 'entity_id', 'entity_type', 'text', 'html', 'parent_id',
            'local_id', 'created_at', 'updated_at', 'created_by',
        ], [
            function (Comment $comment) {
                $comment->createdBy->makeVisible(['email']);
            }
        ]);
    }

    public function create(Request $request)
    {
        $requestData = $this->validate($request, [
            'html'      => ['required', 'string'],
            'parent_id' => ['nullable', 'integer'],
            'page_id' => ['nullable', 'integer'],
        ]);
        $page = null;
        if ($request->has('page_id')) {
            $page = $this->pageQueries->findVisibleById($request->get('page_id'));
        }
        if ($page === null) {
            return response('Not found', 404);
        }
        if ($page->draft) {
            return $this->jsonError(trans('errors.cannot_add_comment_to_draft'), 400);
        }
        // Create a new comment.
        $this->checkPermission('comment-create-all');
        $comment = $this->commentRepo->create($page, $request['html'], $request['parent_id'] ?? null);
        return response()->json($comment->local_id);
    }

}