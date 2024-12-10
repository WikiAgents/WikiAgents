<?php

namespace BookStack\WikiAgents;
use BookStack\Entities\Queries\BookQueries;
use BookStack\Entities\Queries\PageQueries;
use BookStack\Entities\Queries\BookshelfQueries;
use BookStack\Entities\Repos\BookRepo;

use BookStack\Http\Controller;
use BookStack\Http\ApiController;

use BookStack\Http\HttpRequestService;
use Illuminate\Http\JsonResponse;


class BookToShelfAPIController extends ApiController
{
    public function __construct(
        protected BookRepo $bookRepo,
        protected BookQueries $queries,
        protected PageQueries $pageQueries,
        protected BookshelfQueries $shelveQueries,
    ) {
    }

    public function get(string $id): string
    {
        $book = $this->queries->findVisibleByIdOrFail(intval($id));
        $shelfIds = $book->shelves()->select("id", "name")->getResults();
        return $shelfIds;
    }

}
