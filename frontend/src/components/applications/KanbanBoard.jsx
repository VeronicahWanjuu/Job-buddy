import { Box, Typography, Paper, Button } from '@mui/material';
import { Add } from '@mui/icons-material';
import { DragDropContext, Droppable, Draggable } from '@hello-pangea/dnd';
import ApplicationCard from './ApplicationCard';
import { VALID_STATUSES, STATUS_COLORS } from '../../utils/constants';

const KanbanBoard = ({
  groupedApplications,
  onDragEnd,
  onView,
  onEdit,
  onDelete,
  onAddNew,
}) => {
  return (
    <DragDropContext onDragEnd={onDragEnd}>
      <Box sx={{ display: 'flex', gap: 2, overflowX: 'auto', pb: 2 }}>
        {VALID_STATUSES.map((status) => (
          <Droppable droppableId={status} key={status}>
            {(provided, snapshot) => (
              <Paper
                sx={{
                  minWidth: 300,
                  maxWidth: 300,
                  bgcolor: snapshot.isDraggingOver ? 'action.hover' : 'background.paper',
                  transition: 'background-color 0.2s',
                }}
                elevation={2}
              >
                <Box
                  sx={{
                    p: 2,
                    bgcolor: STATUS_COLORS[status],
                    color: 'white',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                  }}
                >
                  <Typography variant="h6">
                    {status} ({groupedApplications[status]?.length || 0})
                  </Typography>
                  {status === 'Planned' && (
                    <Button
                      size="small"
                      onClick={onAddNew}
                      sx={{ color: 'white', minWidth: 'auto', p: 0.5 }}
                    >
                      <Add />
                    </Button>
                  )}
                </Box>

                <Box
                  ref={provided.innerRef}
                  {...provided.droppableProps}
                  sx={{
                    p: 2,
                    minHeight: 500,
                    maxHeight: 'calc(100vh - 300px)',
                    overflowY: 'auto',
                  }}
                >
                  {groupedApplications[status]?.map((app, index) => (
                    <Draggable
                      key={app.id.toString()}
                      draggableId={app.id.toString()}
                      index={index}
                    >
                      {(provided, snapshot) => (
                        <div
                          ref={provided.innerRef}
                          {...provided.draggableProps}
                          {...provided.dragHandleProps}
                          style={{
                            ...provided.draggableProps.style,
                            opacity: snapshot.isDragging ? 0.8 : 1,
                          }}
                        >
                          <ApplicationCard
                            application={app}
                            onView={onView}
                            onEdit={onEdit}
                            onDelete={onDelete}
                          />
                        </div>
                      )}
                    </Draggable>
                  ))}
                  {provided.placeholder}

                  {(!groupedApplications[status] || groupedApplications[status].length === 0) && (
                    <Typography
                      variant="body2"
                      color="text.secondary"
                      sx={{ textAlign: 'center', mt: 4 }}
                    >
                      No applications
                    </Typography>
                  )}
                </Box>
              </Paper>
            )}
          </Droppable>
        ))}
      </Box>
    </DragDropContext>
  );
};

export default KanbanBoard;