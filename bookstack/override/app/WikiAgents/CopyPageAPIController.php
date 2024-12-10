<?php

namespace BookStack\WikiAgents;

use BookStack\Http\ApiController;
use BookStack\Entities\Queries\PageQueries;
use Illuminate\Http\Request;


class CopyPageAPIController extends ApiController
{
    public function __construct(
        protected PageQueries $pageQueries,
    ) {
    }


    public function copy(Request $request)
    {
        $requestData = $this->validate($request, [
            'page_id'      => ['required', 'string'],
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
        return response()->json($comment->id);
    }

}