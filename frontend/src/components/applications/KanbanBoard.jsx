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
      <Box sx={{ display: 'flex', gap: 1.5, overflowX: 'auto', overflowY: 'hidden', height: '100%', pb: 2 }}>
        {VALID_STATUSES.map((status) => (
          <Droppable droppableId={status} key={status}>
            {(provided, snapshot) => (
              <Paper
                sx={{
                  minWidth: 240,
                  maxWidth: 260,
                  flex: '0 0 auto',
                  bgcolor: snapshot.isDraggingOver ? 'action.hover' : 'background.paper',
                  transition: 'background-color 0.2s',
                  display: 'flex',
                  flexDirection: 'column',
                  height: '100%',
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
                    flexShrink: 0,
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
                    flex: 1,
                    overflowY: 'auto',
                    overflowX: 'hidden',
                    minHeight: 0,
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
                    <Box sx={{ 
                      display: 'flex', 
                      flexDirection: 'column', 
                      alignItems: 'center', 
                      justifyContent: 'center', 
                      mt: 4,
                      py: 4,
                    }}>
                      <Box
                        component="svg"
                        sx={{
                          width: 64,
                          height: 64,
                          mb: 2,
                          opacity: 0.3,
                          color: 'text.secondary',
                        }}
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={1.5}
                          d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                        />
                      </Box>
                      <Typography
                        variant="body2"
                        color="text.secondary"
                        sx={{ textAlign: 'center' }}
                      >
                        No applications
                      </Typography>
                    </Box>
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